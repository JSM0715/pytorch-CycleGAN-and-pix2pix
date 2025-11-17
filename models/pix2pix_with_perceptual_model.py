import torch
import torch.nn as nn
from .base_model import BaseModel
from . import networks
import torchvision.models as models


class VGGLoss(nn.Module):
    """Perceptual loss using VGG features"""
    def __init__(self, device):
        super(VGGLoss, self).__init__()
        try:
            # Try new PyTorch API (>= 0.13)
            vgg = models.vgg19(weights=models.VGG19_Weights.IMAGENET1K_V1).features
        except (AttributeError, TypeError):
            try:
                # Try old API with pretrained=True
                vgg = models.vgg19(pretrained=True).features
            except TypeError:
                # Fallback to VGG16 if VGG19 fails
                try:
                    vgg = models.vgg16(weights=models.VGG16_Weights.IMAGENET1K_V1).features
                except (AttributeError, TypeError):
                    vgg = models.vgg16(pretrained=True).features
        
        self.vgg = vgg.to(device).eval()
        # Freeze VGG parameters
        for param in self.vgg.parameters():
            param.requires_grad = False
        
        # Extract features from specific layers
        # VGG19: [1, 6, 11, 20, 29] for relu1_1, relu2_1, relu3_1, relu4_1, relu5_1
        # VGG16: [1, 6, 11, 18, 25] for relu1_1, relu2_1, relu3_1, relu4_1, relu5_1
        # Use common layers that work for both
        self.feature_layers = [1, 6, 11, 20, 29]  # Will work for VGG19, adjust if using VGG16
        self.layer_names = ['relu1_1', 'relu2_1', 'relu3_1', 'relu4_1', 'relu5_1']
        
    def forward(self, x):
        features = []
        for i, layer in enumerate(self.vgg):
            x = layer(x)
            if i in self.feature_layers:
                features.append(x)
        return features


class Pix2PixWithPerceptualModel(BaseModel):
    """Pix2Pix model with perceptual loss to reduce blurring around edited regions.
    
    This model adds VGG-based perceptual loss to the standard pix2pix loss function.
    Perceptual loss helps preserve fine details and reduce blurring by comparing
    high-level features instead of just pixel values.
    """

    @staticmethod
    def modify_commandline_options(parser, is_train=True):
        """Add new dataset-specific options, and rewrite default values for existing options."""
        # changing the default values to match the pix2pix paper
        parser.set_defaults(norm="batch", netG="unet_256", dataset_mode="aligned")
        if is_train:
            parser.set_defaults(pool_size=0, gan_mode="vanilla")
            parser.add_argument("--lambda_L1", type=float, default=100.0, help="weight for L1 loss")
            parser.add_argument("--lambda_perceptual", type=float, default=10.0, help="weight for perceptual loss")
            parser.add_argument("--use_perceptual", action="store_true", help="use perceptual loss")
        return parser

    def __init__(self, opt):
        """Initialize the pix2pix class with perceptual loss."""
        BaseModel.__init__(self, opt)
        # specify the training losses you want to print out
        self.loss_names = ["G_GAN", "G_L1", "G_Perceptual", "D_real", "D_fake"]
        # specify the images you want to save/display
        self.visual_names = ["real_A", "fake_B", "real_B"]
        # specify the models you want to save to the disk
        if self.isTrain:
            self.model_names = ["G", "D"]
        else:
            self.model_names = ["G"]
        self.device = opt.device
        
        # define networks
        self.netG = networks.define_G(opt.input_nc, opt.output_nc, opt.ngf, opt.netG, opt.norm, 
                                     not opt.no_dropout, opt.init_type, opt.init_gain)

        if self.isTrain:
            # define discriminator
            self.netD = networks.define_D(opt.input_nc + opt.output_nc, opt.ndf, opt.netD, 
                                          opt.n_layers_D, opt.norm, opt.init_type, opt.init_gain)
            
            # define loss functions
            self.criterionGAN = networks.GANLoss(opt.gan_mode).to(self.device)
            self.criterionL1 = torch.nn.L1Loss()
            
            # Perceptual loss (VGG)
            self.use_perceptual = getattr(opt, 'use_perceptual', False)
            if self.use_perceptual:
                self.criterionPerceptual = VGGLoss(self.device)
                self.lambda_perceptual = getattr(opt, 'lambda_perceptual', 10.0)
            else:
                self.criterionPerceptual = None
                self.lambda_perceptual = 0.0
            
            # initialize optimizers
            self.optimizer_G = torch.optim.Adam(self.netG.parameters(), lr=opt.lr, betas=(opt.beta1, 0.999))
            self.optimizer_D = torch.optim.Adam(self.netD.parameters(), lr=opt.lr, betas=(opt.beta1, 0.999))
            self.optimizers.append(self.optimizer_G)
            self.optimizers.append(self.optimizer_D)

    def set_input(self, input):
        """Unpack input data from the dataloader and perform necessary pre-processing steps."""
        AtoB = self.opt.direction == "AtoB"
        self.real_A = input["A" if AtoB else "B"].to(self.device)
        self.real_B = input["B" if AtoB else "A"].to(self.device)
        self.image_paths = input["A_paths" if AtoB else "B_paths"]

    def forward(self):
        """Run forward pass; called by both functions <optimize_parameters> and <test>."""
        self.fake_B = self.netG(self.real_A)  # G(A)

    def backward_D(self):
        """Calculate GAN loss for the discriminator"""
        # Fake
        fake_AB = torch.cat((self.real_A, self.fake_B), 1)
        pred_fake = self.netD(fake_AB.detach())
        self.loss_D_fake = self.criterionGAN(pred_fake, False)
        # Real
        real_AB = torch.cat((self.real_A, self.real_B), 1)
        pred_real = self.netD(real_AB)
        self.loss_D_real = self.criterionGAN(pred_real, True)
        # combine loss and calculate gradients
        self.loss_D = (self.loss_D_fake + self.loss_D_real) * 0.5
        self.loss_D.backward()

    def backward_G(self):
        """Calculate GAN, L1, and Perceptual loss for the generator"""
        # First, G(A) should fake the discriminator
        fake_AB = torch.cat((self.real_A, self.fake_B), 1)
        pred_fake = self.netD(fake_AB)
        self.loss_G_GAN = self.criterionGAN(pred_fake, True)
        
        # Second, L1 loss: G(A) = B
        self.loss_G_L1 = self.criterionL1(self.fake_B, self.real_B) * self.opt.lambda_L1
        
        # Third, Perceptual loss
        self.loss_G_Perceptual = 0.0
        if self.use_perceptual and self.criterionPerceptual is not None:
            # Normalize images to [0, 1] for VGG (VGG expects [0, 1] range)
            fake_B_norm = (self.fake_B + 1) / 2.0  # [-1, 1] -> [0, 1]
            real_B_norm = (self.real_B + 1) / 2.0  # [-1, 1] -> [0, 1]
            
            # Get VGG features
            fake_features = self.criterionPerceptual(fake_B_norm)
            real_features = self.criterionPerceptual(real_B_norm)
            
            # Calculate perceptual loss (L1 distance between features)
            perceptual_loss = 0.0
            for fake_feat, real_feat in zip(fake_features, real_features):
                perceptual_loss += torch.nn.functional.l1_loss(fake_feat, real_feat)
            
            self.loss_G_Perceptual = perceptual_loss * self.lambda_perceptual
        
        # combine loss and calculate gradients
        self.loss_G = self.loss_G_GAN + self.loss_G_L1 + self.loss_G_Perceptual
        self.loss_G.backward()

    def optimize_parameters(self):
        self.forward()  # compute fake images: G(A)
        # update D
        self.set_requires_grad(self.netD, True)
        self.optimizer_D.zero_grad()
        self.backward_D()
        self.optimizer_D.step()
        # update G
        self.set_requires_grad(self.netD, False)
        self.optimizer_G.zero_grad()
        self.backward_G()
        self.optimizer_G.step()

