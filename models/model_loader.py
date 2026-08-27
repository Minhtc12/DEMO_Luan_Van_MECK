import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
import io
import os
import time

CLASS_NAMES = [
    "cho-noi-cai-rang", "chua", "dieu-mua-truyen-thong", "don-ca-tai-tu",
    "dua-bo-bay-nui", "le-hoi-nghinh-ong", "nghe-dan-tre", "nghe-det-chieu",
    "nghe-thuat-san-khau-du-ke-khmer", "ok-om-bok", "phong-tuc-cuoi-truyen-thong", "via-ba-chua-xu-nui-sam"
]
NUM_CLASSES = len(CLASS_NAMES)

CONCEPT_NAMES = [
    # 1. Chợ nổi Cái Răng
    "Cây bẹo bằng tre treo trái cây và rau củ trên ghe",
    "Ghe gỗ chở đầy ắp nông sản nhiệt đới",
    "Xuồng gỗ nhỏ bán đồ ăn nóng và thức uống trên sông",
    "Quần áo phơi khô trên ghe thuyền bằng gỗ",
    "Khung cảnh những chiếc ghe gỗ neo đậu san sát nhau trên sông",
    "Tàu lá dừa (lá lợp nhà) khô treo trên cây bẹo",
    
    # 2. Chùa
    "Cổng tam quan đền chùa Phật giáo Á Đông truyền thống",
    "Mái chùa nhiều tầng cong vút lợp ngói vảy cá",
    "Tòa tháp / Bảo tháp Phật giáo nhiều tầng",
    "Hàng cột chùa bằng gỗ lớn và cửa bức bàn truyền thống",
    "Lư hương đồng cỡ lớn đặt giữa sân chùa",
    
    # 3. Điệu múa truyền thống
    "Phụ nữ múa với nón lá và trang phục Áo dài truyền thống",
    "Diễn viên múa đeo chiếc trống đỏ nhỏ nằm ngang quanh eo (Múa Trống Bồng)",
    "Nhóm người nắm tay nhau nhảy múa thành một vòng tròn lớn (Múa Xòe)",
    "Các diễn viên múa gõ ống tre và gậy gỗ vào nhau (Múa Tắc Xình)",
    "Diễn viên múa biểu diễn với dải lụa dài thướt tha và quạt xếp cỡ lớn",
    "Nữ diễn viên múa đội bình gốm trên đầu với các động tác uốn cong cánh tay (Múa Chăm)",
    "Đồng bào dân tộc thiểu số vừa nhảy múa vừa đánh cồng chiêng đồng lớn",
    
    # 4. Đờn ca tài tử
    "Các nhạc công chơi nhạc cụ dây bằng gỗ truyền thống của Việt Nam",
    "Nhạc công chơi đàn hình tròn như mặt trăng (Đàn Kìm/Đàn Nguyệt)",
    "Các nhạc công ngồi khoanh chân trên chiếu lác biểu diễn",
    "Người hát mặc áo lụa truyền thống của miền Nam Việt Nam (Áo bà ba)",
    
    # 5. Đua bò Bảy Núi
    "Cặp bò đua ách chung một càng",
    "Sân đua là ruộng lúa ngập bùn và nước",
    "Bùn và nước bắn tung tóe dữ dội từ những con vật đang chạy",
    "Người điều khiển đứng chân trần trên chiếc bừa gỗ do bò kéo",
    
    # 6. Lễ Hội Nghinh Ông
    "Đoàn tàu cá trang trí rực rỡ cờ lễ hội đầy màu sắc trên biển",
    "Đoàn rước với lọng che và cờ nghi lễ truyền thống",
    "Những người mặc lễ phục truyền thống dâng rượu và hoa",
    "Mô hình Cá Ông (cá voi) khổng lồ diễu hành trên đường phố",
    
    # 7. Nghề đan tre
    "Người thợ thủ công ngồi bệt trên sàn, xung quanh là các nan tre",
    "Các loại rổ rá, nong, nia hình tròn đan bằng tre cỡ lớn",
    "Các ống tre, nứa khô và xanh thô (chưa qua xử lý)",
    "Đôi bàn tay đan các nan tre theo kiểu lồng qua lồng lại (lóng mốt/lóng đôi)",
    "Người dùng dao chẻ và vót nan tre",
    "Phơi nắng nan tre và rổ rá tre đã đan ngoài sân",
    
    # 8. Nghề dệt chiếu
    "Hai người thợ thủ công phối hợp dệt trên khung cửi truyền thống",
    "Khung gỗ dệt chiếu lớn vắt ngang",
    "Những bó lác/cói nhuộm màu đỏ, xanh, vàng rực rỡ",
    "Phơi những cọng lác nhuộm màu sặc sỡ phủ kín sân rộng",
    "Thành phẩm chiếu ngủ dệt với các họa tiết hình học nhiều màu sắc",
    "Những cuộn chiếu lác thành phẩm được bó tròn",
    
    # 9. Nghệ thuật sân khấu Dù kê Khmer
    "Diễn viên mặc trang phục sân khấu đính kim sa và đội mão vàng hình tháp nhọn",
    "Diễn viên với lớp hóa trang khuôn mặt quỷ hoặc người khổng lồ đậm nét",
    "Phông nền sân khấu vẽ cảnh cung điện hoặc khu rừng",
    "Diễn viên cầm đạo cụ vũ khí sân khấu sơn màu vàng hoặc bạc",
    "Diễn viên mặc xà rông (Sampot) truyền thống của Khmer và dải lụa vắt vai",
    "Các diễn viên thực hiện các tư thế võ thuật và chiến đấu kịch tính",
    
    # 10. Ok Om Bok
    "Chiếc ghe Ngo dài bằng gỗ với hàng chục tay chèo đang đua trên sông",
    "Mâm cúng ngoài trời với cốm dẹp, chuối và dừa",
    "Người đút cốm dẹp (mảnh gạo xanh) cho người khác ăn",
    "Những người giã cốm dẹp trong chiếc cối gỗ lớn",
    "Những chiếc đèn nước bằng giấy phát sáng thả trên sông vào ban đêm",
    "Thả những chiếc đèn lồng giấy phát sáng bay lên bầu trời đêm",
    
    # 11. Phong tục cưới truyền thống
    "Hàng người bưng các mâm quả sính lễ cưới truyền thống phủ vải đỏ (Đội bê tráp)",
    "Cô dâu và chú rể mặc Áo dài đỏ truyền thống và đội khăn đóng",
    "Cô dâu mặc trang phục thổ cẩm dân tộc thiểu số với đồ trang sức bạc nặng",
    "Cô dâu chú rể mặc trang phục cưới truyền thống đứng cùng nhau",
    
    # 12. Vía Bà Chúa Xứ Núi Sam
    "Ngôi miếu với mái ngói lưu ly xanh nhiều tầng",
    "Tượng Nữ thần mặc áo bào thêu tinh xảo và đội vương miện vàng",
    "Đám đông mặc lễ phục truyền thống đi trong đoàn rước",
    "Đám đông khiêng một chiếc kiệu gỗ lớn sơn màu vàng mạ"
]
NUM_CONCEPTS = len(CONCEPT_NAMES)

device = torch.device('cpu')

STUDENT_BACKBONES = {
    "mobilenet_v3_large": "MobileNetV3-Large",
    "efficientnet_b0": "EfficientNet-B0",
    "resnet18": "ResNet18",
    "shufflenet_v2_x1_0": "ShuffleNetV2",
    # MỚI THÊM 2 TRÒ THEO YÊU CẦU
    "densenet121": "DenseNet121",        
    "efficientnet_b3": "EfficientNet-B3",
}

TEACHER_BACKBONES = {
    "resnet50": "ResNet50",
    "densenet121": "DenseNet121",
    "efficientnet_b3": "EfficientNet-B3",
    "swin_t": "Swin-T",
    "vit_b_16": "ViT-B/16",
}


def _build_student_backbone(name: str):
    """Trả về (features, pool, in_features) cho các backbone trò."""
    if name == "mobilenet_v3_large":
        m = models.mobilenet_v3_large(weights=None)
        return m.features, m.avgpool, m.classifier[0].in_features
    if name == "efficientnet_b0":
        m = models.efficientnet_b0(weights=None)
        return m.features, m.avgpool, m.classifier[1].in_features
    if name == "resnet18":
        m = models.resnet18(weights=None)
        features = nn.Sequential(*list(m.children())[:-2])
        return features, nn.AdaptiveAvgPool2d(1), m.fc.in_features
    if name == "shufflenet_v2_x1_0":
        m = models.shufflenet_v2_x1_0(weights=None)
        features = nn.Sequential(m.conv1, m.maxpool, m.stage2, m.stage3, m.stage4, m.conv5)
        return features, nn.AdaptiveAvgPool2d(1), m.fc.in_features
    # MỚI THÊM CƠ CHẾ CẮT LỚP CỦA DENSENET VÀ EFFICIENTNET B3
    if name == "densenet121":
        m = models.densenet121(weights=None)
        # DenseNet cần ReLU trước khi Pool
        pool = nn.Sequential(nn.ReLU(inplace=True), nn.AdaptiveAvgPool2d(1))
        return m.features, pool, m.classifier.in_features
    if name == "efficientnet_b3":
        m = models.efficientnet_b3(weights=None)
        return m.features, m.avgpool, m.classifier[1].in_features
    raise ValueError(f"Backbone trò không hỗ trợ: {name}")


def _build_teacher(name: str, num_classes: int) -> nn.Module:
    """Trả về mạng giáo viên full-size với lớp phân loại đã thay cho num_classes."""
    if name == "resnet50":
        m = models.resnet50(weights=None)
        m.fc = nn.Linear(m.fc.in_features, num_classes)
    elif name == "densenet121":
        m = models.densenet121(weights=None)
        m.classifier = nn.Linear(m.classifier.in_features, num_classes)
    elif name == "efficientnet_b3":
        m = models.efficientnet_b3(weights=None)
        m.classifier[1] = nn.Linear(m.classifier[1].in_features, num_classes)
    elif name == "swin_t":
        m = models.swin_t(weights=None)
        m.head = nn.Linear(m.head.in_features, num_classes)
    elif name == "vit_b_16":
        m = models.vit_b_16(weights=None)
        m.heads.head = nn.Linear(m.heads.head.in_features, num_classes)
    else:
        raise ValueError(f"Backbone thầy không hỗ trợ: {name}")
    return m


def _build_plain_student(name: str, num_classes: int) -> nn.Module:
    """Trò 'hộp đen' — GIỮ NGUYÊN classifier gốc của torchvision."""
    if name == "mobilenet_v3_large":
        m = models.mobilenet_v3_large(weights=None)
        m.classifier[3] = nn.Linear(m.classifier[3].in_features, num_classes)
    elif name == "efficientnet_b0":
        m = models.efficientnet_b0(weights=None)
        m.classifier[1] = nn.Linear(m.classifier[1].in_features, num_classes)
    elif name == "resnet18":
        m = models.resnet18(weights=None)
        m.fc = nn.Linear(m.fc.in_features, num_classes)
    elif name == "shufflenet_v2_x1_0":
        m = models.shufflenet_v2_x1_0(weights=None)
        m.fc = nn.Linear(m.fc.in_features, num_classes)
    # MỚI THÊM LINEAR CLASSIFIER CHO TRÒ DENSENET VÀ EFFICIENTNET B3
    elif name == "densenet121":
        m = models.densenet121(weights=None)
        m.classifier = nn.Linear(m.classifier.in_features, num_classes)
    elif name == "efficientnet_b3":
        m = models.efficientnet_b3(weights=None)
        m.classifier[1] = nn.Linear(m.classifier[1].in_features, num_classes)
    else:
        raise ValueError(f"Backbone trò không hỗ trợ: {name}")
    return m


class StudentCBM(nn.Module):
    """Trò kiến trúc Concept Bottleneck Model - dùng cho các mức có CBM / MECK."""
    def __init__(self, backbone_name, num_classes, num_concepts):
        super().__init__()
        self.features, self.pool, in_features = _build_student_backbone(backbone_name)
        self.concept_layer = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.Hardswish(inplace=True),
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(512, num_concepts)
        )
        self.classifier = nn.Linear(num_concepts, num_classes)

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x)
        x = torch.flatten(x, 1)
        concept_logits = self.concept_layer(x)
        concept_probs = torch.sigmoid(concept_logits)
        class_logits = self.classifier(concept_probs)
        return concept_probs, class_logits


STAGES = [
    {"id": "baseline",      "order": 1, "label": "1. Baseline (Học trực tiếp)",                    "is_cbm": False, "teacher": None},
    {"id": "kd1",            "order": 2, "label": "2. Chưng cất từ 1 Thầy",                          "is_cbm": False, "teacher": "single"},
    {"id": "kd5_ensemble",   "order": 3, "label": "3a. Chưng cất 5 Thầy - Định tuyến Mềm (Ensemble)","is_cbm": False, "teacher": "ensemble"},
    {"id": "kd5_expert",     "order": 4, "label": "3b. Chưng cất 5 Thầy - Định tuyến Cứng (Expert)", "is_cbm": False, "teacher": "expert"},
    {"id": "cbm1",           "order": 5, "label": "4a. 1 Thầy + CBM",                                "is_cbm": True,  "teacher": "single"},
    {"id": "cbm5_ensemble",  "order": 6, "label": "4b. 5 Thầy (Ensemble) + CBM",                     "is_cbm": True,  "teacher": "ensemble"},
    {"id": "cbm5_expert",    "order": 7, "label": "4c. 5 Thầy (Expert) + CBM",                       "is_cbm": True,  "teacher": "expert"},
    {"id": "meck1",          "order": 8, "label": "5a. 1 Thầy + CBM + LLM",                          "is_cbm": True,  "teacher": "single"},
    {"id": "meck5_ensemble", "order": 9, "label": "5b. MECK: 5 Thầy (Ensemble) + CBM + LLM", "is_cbm": True, "teacher": "ensemble"},
    {"id": "meck5_expert",   "order": 10, "label": "5c. 5 Thầy (Expert) + CBM + LLM",                "is_cbm": True,  "teacher": "expert"},
]
STAGE_BY_ID = {s["id"]: s for s in STAGES}

STAGE_SHORT_PREFIX = {
    "baseline": "Baseline",
    "kd1": "KD", "kd5_ensemble": "KD", "kd5_expert": "KD",
    "cbm1": "CBM", "cbm5_ensemble": "CBM", "cbm5_expert": "CBM",
    "meck1": "MECK", "meck5_ensemble": "MECK", "meck5_expert": "MECK",
}
STAGE_ROUTING_SUFFIX = {
    "kd5_ensemble": "Ensemble", "kd5_expert": "Expert",
    "cbm5_ensemble": "Ensemble", "cbm5_expert": "Expert",
    "meck5_ensemble": "Ensemble", "meck5_expert": "Expert",
}


REF_METRICS = {
    # ---- Teacher (mục 4.2.1) ----
    ("teacher", "resnet50"):        {"precision": 0.9523, "recall": 0.9495, "f1": 0.9503, "acc": 0.9530, "size_mb": 90.075},
    ("teacher", "densenet121"):     {"precision": 0.9450, "recall": 0.9443, "f1": 0.9435, "acc": 0.9446, "size_mb": 27.157},
    ("teacher", "efficientnet_b3"): {"precision": 0.9647, "recall": 0.9643, "f1": 0.9642, "acc": 0.9640, "size_mb": 41.410},
    ("teacher", "swin_t"):          {"precision": 0.9580, "recall": 0.9582, "f1": 0.9576, "acc": 0.9585, "size_mb": 105.297},
    ("teacher", "vit_b_16"):        {"precision": 0.9606, "recall": 0.9602, "f1": 0.9599, "acc": 0.9613, "size_mb": 327.390},

    # ---- Baseline (mục 4.2.2) ----
    ("baseline", "efficientnet_b0"):     {"precision": 0.9562, "recall": 0.9567, "f1": 0.9561, "acc": 0.9576, "size_mb": 15.639},
    ("baseline", "mobilenet_v3_large"):  {"precision": 0.9237, "recall": 0.9229, "f1": 0.9220, "acc": 0.9234, "size_mb": 16.291},
    ("baseline", "resnet18"):            {"precision": 0.9376, "recall": 0.9353, "f1": 0.9357, "acc": 0.9373, "size_mb": 42.736},
    ("baseline", "shufflenet_v2_x1_0"):  {"precision": 0.9246, "recall": 0.9250, "f1": 0.9238, "acc": 0.9253, "size_mb": 5.001},

    # ---- KD 1 Thầy (mục 4.2.3.a / Bảng 4.4) ----
    ("kd1", "efficientnet_b0"):    {"precision": 0.9600, "recall": 0.9592, "f1": 0.9592, "acc": 0.9603, "size_mb": 15.639, "teacher_used": "EfficientNet-B3"},
    ("kd1", "mobilenet_v3_large"): {"precision": 0.9486, "recall": 0.9480, "f1": 0.9479, "acc": 0.9483, "size_mb": 16.292, "teacher_used": "EfficientNet-B3"},
    ("kd1", "resnet18"):           {"precision": 0.9462, "recall": 0.9459, "f1": 0.9455, "acc": 0.9474, "size_mb": 42.736, "teacher_used": "ResNet50"},
    ("kd1", "shufflenet_v2_x1_0"): {"precision": 0.9373, "recall": 0.9366, "f1": 0.9362, "acc": 0.9382, "size_mb": 5.001,  "teacher_used": "ResNet50"},
    ("kd1", "densenet121"):        {"precision": 0.9543, "recall": 0.9526, "f1": 0.9526, "acc": 0.9539, "size_mb": 27.164, "teacher_used": "DenseNet121"},
    ("kd1", "efficientnet_b3"):    {"precision": 0.9678, "recall": 0.9674, "f1": 0.9673, "acc": 0.9677, "size_mb": 41.416, "teacher_used": "EfficientNet-B3"},

    # ---- KD 5 Thầy - Ensemble Softmax (Bảng 4.5) ----
    ("kd5_ensemble", "efficientnet_b0"):    {"precision": 0.9641, "recall": 0.9641, "f1": 0.9639, "acc": 0.9649, "size_mb": 15.637},
    ("kd5_ensemble", "mobilenet_v3_large"): {"precision": 0.9585, "recall": 0.9584, "f1": 0.9579, "acc": 0.9585, "size_mb": 16.290},
    ("kd5_ensemble", "resnet18"):           {"precision": 0.9431, "recall": 0.9417, "f1": 0.9417, "acc": 0.9437, "size_mb": 42.735},
    ("kd5_ensemble", "shufflenet_v2_x1_0"): {"precision": 0.9407, "recall": 0.9388, "f1": 0.9392, "acc": 0.9400, "size_mb": 4.998},

    # ---- KD 5 Thầy - Expert Hard Routing (Bảng 4.6) ----
    ("kd5_expert", "efficientnet_b0"):    {"precision": 0.9606, "recall": 0.9607, "f1": 0.9604, "acc": 0.9613, "size_mb": 15.639},
    ("kd5_expert", "mobilenet_v3_large"): {"precision": 0.9511, "recall": 0.9506, "f1": 0.9504, "acc": 0.9511, "size_mb": 16.292},
    ("kd5_expert", "resnet18"):           {"precision": 0.9469, "recall": 0.9454, "f1": 0.9455, "acc": 0.9474, "size_mb": 42.736},
    ("kd5_expert", "shufflenet_v2_x1_0"): {"precision": 0.9416, "recall": 0.9392, "f1": 0.9398, "acc": 0.9410, "size_mb": 5.001},

    # ---- CBM 1 Thầy (Bảng 4.7) ----
    ("cbm1", "efficientnet_b0"):    {"precision": 0.9569, "recall": 0.9570, "f1": 0.9566, "acc": 0.9576, "size_mb": 18.156, "teacher_used": "Swin-T"},
    ("cbm1", "mobilenet_v3_large"): {"precision": 0.9514, "recall": 0.9499, "f1": 0.9500, "acc": 0.9511, "size_mb": 13.490, "teacher_used": "Swin-T"},
    ("cbm1", "resnet18"):           {"precision": 0.9405, "recall": 0.9389, "f1": 0.9391, "acc": 0.9410, "size_mb": 43.789, "teacher_used": "ViT-B/16"},
    ("cbm1", "shufflenet_v2_x1_0"): {"precision": 0.9410, "recall": 0.9405, "f1": 0.9403, "acc": 0.9428, "size_mb": 7.032,  "teacher_used": "ViT-B/16"},
    ("cbm1", "densenet121"):        {"precision": 0.9443, "recall": 0.9440, "f1": 0.9435, "acc": 0.9446, "size_mb": 29.246, "teacher_used": "DenseNet121"},
    ("cbm1", "efficientnet_b3"):    {"precision": 0.9615, "recall": 0.9597, "f1": 0.9603, "acc": 0.9613, "size_mb": 44.474, "teacher_used": "EfficientNet-B3"},

    # ---- CBM 5 Thầy Ensemble (Bảng 4.8) ----
    ("cbm5_ensemble", "efficientnet_b0"):    {"precision": 0.9586, "recall": 0.9589, "f1": 0.9585, "acc": 0.9594, "size_mb": 18.209},
    ("cbm5_ensemble", "mobilenet_v3_large"): {"precision": 0.9535, "recall": 0.9521, "f1": 0.9525, "acc": 0.9530, "size_mb": 13.543},
    ("cbm5_ensemble", "resnet18"):           {"precision": 0.9417, "recall": 0.9414, "f1": 0.9411, "acc": 0.9428, "size_mb": 43.841},
    ("cbm5_ensemble", "shufflenet_v2_x1_0"): {"precision": 0.9440, "recall": 0.9428, "f1": 0.9431, "acc": 0.9456, "size_mb": 7.085},

    # ---- CBM 5 Thầy Expert (Bảng 4.9) ----
    ("cbm5_expert", "efficientnet_b0"):    {"precision": 0.9561, "recall": 0.9562, "f1": 0.9558, "acc": 0.9566, "size_mb": 18.209},
    ("cbm5_expert", "mobilenet_v3_large"): {"precision": 0.9496, "recall": 0.9473, "f1": 0.9479, "acc": 0.9483, "size_mb": 13.543},
    ("cbm5_expert", "resnet18"):           {"precision": 0.9401, "recall": 0.9379, "f1": 0.9382, "acc": 0.9400, "size_mb": 43.841},
    ("cbm5_expert", "shufflenet_v2_x1_0"): {"precision": 0.9294, "recall": 0.9270, "f1": 0.9276, "acc": 0.9299, "size_mb": 7.084},

    # ---- MECK 1 Thầy (Bảng 4.10) ----
    ("meck1", "efficientnet_b0"):    {"precision": 0.9589, "recall": 0.9586, "f1": 0.9585, "acc": 0.9594, "size_mb": 18.213, "teacher_used": "EfficientNet-B3"},
    ("meck1", "mobilenet_v3_large"): {"precision": 0.9452, "recall": 0.9418, "f1": 0.9426, "acc": 0.9437, "size_mb": 13.551, "teacher_used": "EfficientNet-B3"},
    ("meck1", "resnet18"):           {"precision": 0.9402, "recall": 0.9387, "f1": 0.9391, "acc": 0.9410, "size_mb": 43.842, "teacher_used": "ResNet50"},
    ("meck1", "shufflenet_v2_x1_0"): {"precision": 0.9371, "recall": 0.9356, "f1": 0.9360, "acc": 0.9382, "size_mb": 7.090,  "teacher_used": "ResNet50"},
    ("meck1", "densenet121"):        {"precision": 0.9520, "recall": 0.9526, "f1": 0.9517, "acc": 0.9530, "size_mb": 29.252, "teacher_used": "DenseNet121"},
    ("meck1", "efficientnet_b3"):    {"precision": 0.9655, "recall": 0.9643, "f1": 0.9647, "acc": 0.9659, "size_mb": 44.484, "teacher_used": "EfficientNet-B3"},

    # ---- MECK 5 Thầy Ensemble (Bảng 4.11) — cấu hình đề xuất của luận văn ----
    ("meck5_ensemble", "efficientnet_b0"):    {"precision": 0.9609, "recall": 0.9616, "f1": 0.9610, "acc": 0.9622, "size_mb": 18.211},
    ("meck5_ensemble", "mobilenet_v3_large"): {"precision": 0.9546, "recall": 0.9518, "f1": 0.9526, "acc": 0.9530, "size_mb": 13.551},
    ("meck5_ensemble", "resnet18"):           {"precision": 0.9468, "recall": 0.9442, "f1": 0.9449, "acc": 0.9456, "size_mb": 43.842},
    ("meck5_ensemble", "shufflenet_v2_x1_0"): {"precision": 0.9472, "recall": 0.9456, "f1": 0.9459, "acc": 0.9474, "size_mb": 7.090},

    # ---- MECK 5 Thầy Expert (Bảng 4.12) ----
    ("meck5_expert", "efficientnet_b0"):    {"precision": 0.9607, "recall": 0.9605, "f1": 0.9604, "acc": 0.9613, "size_mb": 18.213},
    ("meck5_expert", "mobilenet_v3_large"): {"precision": 0.9542, "recall": 0.9508, "f1": 0.9518, "acc": 0.9530, "size_mb": 13.551},
    ("meck5_expert", "resnet18"):           {"precision": 0.9523, "recall": 0.9511, "f1": 0.9515, "acc": 0.9530, "size_mb": 43.842},
    ("meck5_expert", "shufflenet_v2_x1_0"): {"precision": 0.9441, "recall": 0.9411, "f1": 0.9420, "acc": 0.9446, "size_mb": 7.090},
}


CHECKPOINT_DIR = "checkpoints"

def _normalize(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum())

def _list_checkpoint_files_normalized():
    try:
        return {_normalize(f): f for f in os.listdir(CHECKPOINT_DIR)}
    except FileNotFoundError:
        return {}

_CKPT_FILES_NORMALIZED = _list_checkpoint_files_normalized()

BACKBONE_NAME_ALIASES = {
    "resnet50": ["resnet50"],
    "densenet121": ["densenet121"],
    "efficientnet_b3": ["efficientnet_b3", "effnetb3", "efficientnetb3"],
    "swin_t": ["swin_t", "swint"],
    "vit_b_16": ["vit_b_16", "vitb16"],
    "mobilenet_v3_large": ["mobilenet_v3_large", "mobilenetv3large"],
    "efficientnet_b0": ["efficientnet_b0", "effnetb0", "efficientnetb0"],
    "resnet18": ["resnet18"],
    "shufflenet_v2_x1_0": ["shufflenet_v2_x1_0", "shufflenetv2"],
}


def ckpt(prefix: str, backbone: str) -> str:
    for bb_alias in BACKBONE_NAME_ALIASES.get(backbone, [backbone]):
        wanted = _normalize(f"{prefix}_{bb_alias}_best.pth")
        real_name = _CKPT_FILES_NORMALIZED.get(wanted)
        if real_name:
            return os.path.join(CHECKPOINT_DIR, real_name)
    return os.path.join(CHECKPOINT_DIR, f"{prefix}_{backbone}_best.pth")


MODEL_REGISTRY = {}

# --- Thầy ---
for bb_key, bb_label in TEACHER_BACKBONES.items():
    ref = REF_METRICS.get(("teacher", bb_key), {})
    key = f"teacher_{bb_key}"
    MODEL_REGISTRY[key] = {
        "name": f"Thầy: {bb_label} (Hộp đen)",
        "kind": "teacher",
        "backbone": bb_key,
        "backbone_label": bb_label,
        "group": "teacher",
        "group_label": "Hội đồng Giáo viên — Mô hình Tham chiếu (Ceiling, ngoài chuỗi chưng cất)",
        "group_order": 99,
        "is_cbm": False,
        "weights": ckpt("teacher", bb_key),
        "size": f'{ref.get("size_mb", "?")} MB',
        "ref_metrics": ref,
    }

# --- Trò ---
for stage in STAGES:
    for bb_key, bb_label in STUDENT_BACKBONES.items():
        
        # ĐIỀU KIỆN LỌC RIÊNG: Chỉ đăng ký DenseNet121 và Eff-B3 vào 3 giai đoạn "1 Thầy"
        if bb_key in ["densenet121", "efficientnet_b3"]:
            if stage["id"] not in ["kd1", "cbm1", "meck1"]:
                continue

        ref = REF_METRICS.get((stage["id"], bb_key), {})
        key = f"{stage['id']}_{bb_key}"
        short_prefix = STAGE_SHORT_PREFIX.get(stage["id"], "")
        sep = ": " if short_prefix == "MECK" else " - "
        
        if ref.get("teacher_used"):
            suffix = f" (Thầy: {ref['teacher_used']})"
        elif stage["id"] in STAGE_ROUTING_SUFFIX:
            suffix = f" ({STAGE_ROUTING_SUFFIX[stage['id']]})"
        else:
            suffix = ""
            
        MODEL_REGISTRY[key] = {
            "name": f"{short_prefix}{sep}{bb_label}{suffix}",
            "kind": "cbm" if stage["is_cbm"] else "plain",
            "backbone": bb_key,
            "backbone_label": bb_label,
            "group": stage["id"],
            "group_label": stage["label"],
            "group_order": stage["order"],
            "is_cbm": stage["is_cbm"],
            "weights": ckpt(stage["id"], bb_key),
            "size": f'{ref.get("size_mb", "?")} MB',
            "ref_metrics": ref,
        }


def load_all_models():
    print(f"Đang khởi tạo {len(MODEL_REGISTRY)} mô hình đã đăng ký...")
    loaded_models = {}

    for key, info in MODEL_REGISTRY.items():
        try:
            if info["kind"] == "teacher":
                model = _build_teacher(info["backbone"], NUM_CLASSES)
            elif info["kind"] == "cbm":
                model = StudentCBM(info["backbone"], NUM_CLASSES, NUM_CONCEPTS)
            else:  
                model = _build_plain_student(info["backbone"], NUM_CLASSES)

            model.load_state_dict(torch.load(info["weights"], map_location=device))
            model.eval()
            loaded_models[key] = model
            print(f"[OK] Đã tải: {info['name']}")
        except FileNotFoundError:
            print(f"[BỎ QUA] Chưa có checkpoint cho: {info['name']} ({info['weights']})")
        except Exception as e:
            print(f"[CẢNH BÁO] Lỗi khi tải {info['name']}: {e}")

    return loaded_models


def _get_transform():
    from torchvision import transforms
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])


def predict_image(model_key, loaded_models_dict, image_bytes):
    model = loaded_models_dict[model_key]
    info = MODEL_REGISTRY[model_key]

    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    input_tensor = _get_transform()(image).unsqueeze(0).to(device)

    start_time = time.time()

    with torch.no_grad():
        if info["kind"] == "cbm":
            concept_probs, class_logits = model(input_tensor)
            concepts_dict = dict(zip(CONCEPT_NAMES, concept_probs[0].tolist()))
            top_concepts = dict(sorted(concepts_dict.items(), key=lambda item: item[1], reverse=True)[:6])
        else:
            class_logits = model(input_tensor)
            top_concepts = None

        probs = torch.nn.functional.softmax(class_logits[0], dim=0)

        top3_probs, top3_indices = torch.topk(probs, 3)
        top3_results = [
            {"label": CLASS_NAMES[idx.item()], "prob": prob.item()}
            for prob, idx in zip(top3_probs, top3_indices)
        ]

        confidence = top3_probs[0].item()
        predicted_class = CLASS_NAMES[top3_indices[0].item()]

    inference_time_ms = (time.time() - start_time) * 1000

    return {
        "prediction": predicted_class,
        "confidence": confidence,
        "top_3": top3_results,
        "inference_time_ms": inference_time_ms,
        "metrics": {"size": info["size"]},
        "concepts": top_concepts,
    }