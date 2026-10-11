import torch
import torch.nn as nn
import torchvision.models as models


class ChannelAttention(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(c, c//16),
            nn.ReLU(),
            nn.Linear(c//16, c),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y


class SpatialAttention(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, 7, padding=3)

    def forward(self, x):
        avg = torch.mean(x, 1, keepdim=True)
        mx, _ = torch.max(x, 1, keepdim=True)
        attn = torch.sigmoid(self.conv(torch.cat([avg, mx], 1)))
        return x * attn


class HbDualModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.f_net = models.efficientnet_b0(weights='DEFAULT').features
        self.p_net = models.efficientnet_b0(weights='DEFAULT').features

        self.ca_f = ChannelAttention(1280)
        self.ca_p = ChannelAttention(1280)

        self.sa_f = SpatialAttention()
        self.sa_p = SpatialAttention()

        self.pool = nn.AdaptiveAvgPool2d(1)

        self.regressor = nn.Sequential(
            nn.Linear(2560 + 2, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 1)
        )

        self.classifier = nn.Sequential(
            nn.Linear(2560, 128),
            nn.ReLU(),
            nn.Linear(128, 3)
        )

        self.color_head = nn.Sequential(
            nn.Linear(2560, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, f, p, extra):
        f = self.sa_f(self.ca_f(self.f_net(f)))
        p = self.sa_p(self.ca_p(self.p_net(p)))

        f = self.pool(f).view(f.size(0), -1)
        p = self.pool(p).view(p.size(0), -1)

        combined = torch.cat([f, p], dim=1)

        hb = self.regressor(torch.cat([combined, extra], dim=1))
        cls = self.classifier(combined)
        color = self.color_head(combined)

        return hb, color, cls