import torch
import torch.nn.functional as F

def create_window(window_size, channel):
    _1D_window = torch.hann_window(window_size).unsqueeze(1)
    _2D_window = _1D_window.mm(_1D_window.t()).float().unsqueeze(0).unsqueeze(0)
    window = _2D_window.repeat(channel, 1, 1, 1)  # Repeat the window for each channel
    return window.to(torch.float32)

def ssim_structural(img1, img2, window_size, size_average=True, eps=1e-8):
    channel = img1.size(1)
    window = create_window(window_size, channel).to(img1.device)
    window = window / window.sum()

    mu1 = F.conv2d(img1, window, padding=window_size//2, groups=channel)
    mu2 = F.conv2d(img2, window, padding=window_size//2, groups=channel)

    sigma1_sq = F.conv2d(img1 * img1, window, padding=window_size//2, groups=channel) - mu1.pow(2)
    sigma2_sq = F.conv2d(img2 * img2, window, padding=window_size//2, groups=channel) - mu2.pow(2)
    sigma12 = F.conv2d(img1 * img2, window, padding=window_size//2, groups=channel) - mu1 * mu2

    structural_similarity = (sigma12 + eps) / (torch.sqrt(sigma1_sq * sigma2_sq) + eps)

    # Average the structural similarity over all channels
    if size_average:
        return structural_similarity.mean()
    else:
        return structural_similarity.view(channel, -1).mean(-1)

class StructuralLoss(torch.nn.Module):
    def __init__(self, window_size=11, size_average=True):
        super(StructuralLoss, self).__init__()
        self.window_size = window_size
        self.size_average = size_average

    def forward(self, img1, img2):
        return 1 - ssim_structural(img1, img2, self.window_size, self.size_average)

# # Usage of Structural Loss
# img1 = torch.randn(1, 3, 256, 256)  # Example tensor
# img2 = torch.randn(1, 3, 256, 256)  # Example tensor

# structural_loss = StructuralLoss(window_size=11, size_average=True)
# loss = structural_loss(img1, img2)

# print(f"Structural Loss: {loss.item()}")