# 基于局部特征描述子的指纹识别方法研究综述

## 摘要

指纹识别是生物特征识别（Biometric Recognition，生物特征识别）领域中应用最广泛的身份认证技术之一，长期应用于刑侦鉴定、门禁系统、移动终端解锁、金融支付和人员身份核验等场景。传统指纹识别方法主要依赖细节点（Minutiae，细节点）特征，例如脊线端点和脊线分叉点，这类方法具有较强的可解释性和较高的工程成熟度，是自动指纹识别系统（Automated Fingerprint Identification System，自动指纹识别系统）中的核心技术。然而，在低质量指纹、小面积指纹、残缺指纹和非接触式指纹等复杂场景下，单纯依赖细节点坐标和方向往往难以获得稳定匹配结果。近年来，随着深度学习（Deep Learning，深度学习）技术的发展，卷积神经网络（Convolutional Neural Network，卷积神经网络）、孪生网络（Siamese Network，孪生网络）、深度局部描述子（Deep Local Descriptor，深度局部描述子）和固定长度深度表示等方法逐渐被引入指纹识别任务中，为提升复杂场景下的识别鲁棒性提供了新的技术路线。本文围绕指纹识别基础、指纹图像预处理、细节点提取与匹配、传统局部特征描述子、SIFT（Scale-Invariant Feature Transform，尺度不变特征变换）方法、深度学习指纹表示和局部图块（Patch，局部图块）描述子等方向进行文献综述，并分析当前方法在关键点稳定性、纹理重复性、样本构造、模型泛化能力、可解释性和安全性方面的挑战。研究认为，未来指纹识别技术将更多采用“细节点锚定 + 深度局部描述子 + 全局几何验证”的混合框架，以兼顾识别精度、鲁棒性和可解释性。

**关键词：** 指纹识别；细节点；局部描述子；SIFT；深度学习；孪生网络；生物特征识别

## 1 引言

指纹识别是一种利用人类手指表面脊线纹理进行身份认证的生物特征识别技术。由于指纹具有较强的个体差异性、长期稳定性和采集便利性，它在公共安全、司法鉴定、考勤门禁、手机解锁和金融身份认证等领域得到了广泛应用。Maltoni 等在《Handbook of Fingerprint Recognition》中系统总结了指纹识别系统的传感器技术、图像增强、特征提取、匹配算法、性能评估和系统安全问题，指出指纹识别方法大体可以分为基于细节点的方法、基于纹理的方法、基于相关性的方法和混合匹配方法[1]。

传统自动指纹识别系统主要依赖细节点特征。细节点通常包括脊线端点（Ridge Ending，脊线端点）和脊线分叉点（Bifurcation，脊线分叉点）。与直接比较整幅指纹图像相比，细节点表示更加紧凑，计算效率较高，也更符合人工指纹鉴定中的经验。Jain 等较早研究了在线指纹验证方法，并提出利用指纹局部特征实现自动身份验证[3]。随后，基于滤波器组的指纹匹配方法进一步增强了对指纹纹理结构的表达能力[4]。FVC（Fingerprint Verification Competition，指纹验证竞赛）系列评测推动了指纹验证算法在公开数据集上的标准化比较，为后续研究提供了重要评价基础[5-8]。

尽管基于细节点的指纹识别方法已经较为成熟，但在实际应用中仍面临多种困难。首先，指纹图像质量会受到采集设备、手指湿度、按压力度、皮肤破损、污渍和运动模糊等因素影响。其次，小面积指纹和残缺指纹往往只包含局部纹理区域，细节点数量不足，难以建立可靠的全局匹配关系。再次，非接触式指纹采集虽然在卫生性和用户体验方面具有优势，但其成像角度、尺度和形变更加复杂，给传统算法带来更大挑战。

近年来，深度学习为指纹识别提供了新的研究思路。研究者开始使用卷积神经网络进行指纹增强、细节点检测、方向场估计和特征嵌入学习。例如，MinutiaeNet（细节点网络）将深度网络与指纹领域知识结合，用于自动细节点提取[14-15]；DeepPrint（深度指纹表示）尝试学习固定长度指纹特征向量，用紧凑表示完成指纹匹配[17]；MinNet（细节点图块嵌入网络）则将局部图块深度嵌入用于潜指纹识别任务[18]。这些研究说明，深度学习方法能够在一定程度上弥补传统手工特征设计的不足。

因此，本文以“基于局部特征描述子的指纹识别方法”为综述主题，重点分析传统细节点方法、SIFT 局部描述子、深度学习局部描述子和小面积指纹识别中的关键问题。本文的主要目标不是全面覆盖指纹识别所有分支，而是围绕“局部特征如何被提取、描述和匹配”这一主线展开讨论。

## 2 指纹识别技术基础

### 2.1 指纹图像结构与特征层级

指纹图像主要由脊线（Ridge，脊线）和谷线（Valley，谷线）构成。脊线在图像中通常表现为较暗或较亮的连续纹理，而谷线则是脊线之间的间隔区域。根据特征的细节程度，指纹特征通常可以划分为三个层级。

第一层级是全局结构特征，包括核心点（Core Point，核心点）、三角点（Delta Point，三角点）和整体纹型，例如弓型纹、箕型纹和斗型纹。这类特征主要用于指纹分类和粗匹配，能够帮助系统缩小候选搜索范围，但通常不足以单独完成高精度身份识别。

第二层级是细节点特征，主要包括脊线端点和脊线分叉点。细节点具有较好的稳定性和判别性，是自动指纹识别系统中最常用的特征类型。基于细节点的模板通常记录每个细节点的位置、方向、类型和质量分数，后续匹配时通过比较两组细节点之间的空间关系来判断是否来自同一手指。

第三层级是更精细的脊线细节，例如汗孔（Pore，汗孔）、脊线边缘形状、脊线宽度和细微纹理变化等。这类特征具有更高的判别能力，但对图像分辨率要求较高，通常需要高质量、高分辨率图像才能稳定提取。因此，在常见 500 dpi（Dots Per Inch，每英寸点数）指纹图像中，细节点仍然是最重要、最实用的特征层级。

### 2.2 指纹图像预处理

指纹图像预处理是指纹识别流程中的基础环节，通常包括图像分割、图像增强、方向场估计、脊线频率估计、二值化、细化和伪细节点去除等步骤。Hong、Wan 和 Jain 提出的指纹图像增强方法是传统指纹增强中的经典工作，该方法利用局部脊线方向和脊线频率构造 Gabor 滤波器（Gabor Filter，Gabor 滤波器），从而增强脊线与谷线之间的对比度[2]。Yang 等进一步改进了 Gabor 滤波器设计方法，提高了对不同指纹质量区域的适应能力[24]。

预处理质量会直接影响后续特征提取效果。如果图像增强不足，真实脊线结构可能不清晰，导致细节点漏检；如果增强过度，噪声区域可能被错误强化，产生伪细节点。对于低质量指纹和残缺指纹，方向场估计尤其重要，因为方向场错误会导致后续增强和细化过程出现结构扭曲。Yoon、Feng 和 Jain 针对潜指纹增强提出了鲁棒方向场估计方法，说明方向场建模对于复杂指纹图像具有重要意义[20]。

### 2.3 细节点提取与匹配流程

传统细节点提取通常包括图像增强、二值化、脊线细化、交叉数检测和伪细节点去除等步骤。交叉数方法通过统计某一像素邻域内脊线连接数判断该点是否为端点或分叉点。虽然该方法结构简单、可解释性强，但对图像质量较为敏感。

细节点匹配通常需要解决平移、旋转、尺度变化和非线性皮肤形变问题。常见流程包括局部匹配和全局匹配两个阶段。局部匹配首先判断单个细节点及其邻域结构是否相似，全局匹配再估计两枚指纹之间的整体变换关系，并验证候选细节点对是否满足几何一致性。Ross 等提出的可变形模型方法尝试处理指纹匹配中的非线性形变问题[23]；Chen 等则使用归一化模糊相似度处理扭曲指纹匹配[22]。这些研究说明，指纹匹配不仅是特征比较问题，也是几何变换和形变建模问题。

## 3 传统局部特征描述子方法

### 3.1 基于细节点邻域的局部描述子

细节点不仅可以通过坐标和方向表示，也可以结合其邻域结构构造局部描述子。细节点邻域描述子通常描述中心细节点周围其他细节点的相对位置、方向差异、距离分布和局部纹理信息。与单独使用细节点坐标相比，局部描述子能够提供更丰富的判别信息，并提高候选细节点匹配的准确性。

Peralta 等对基于细节点的局部匹配方法进行了系统综述，将相关方法从特征构造、匹配策略和实验评价等方面进行了分类[9]。该研究指出，局部细节点匹配方法在验证和识别任务中具有较好的准确率与计算效率平衡。Feng 和 Zhou 对多种细节点描述子进行了性能评价，指出局部描述子的稳定性会直接影响最终匹配结果[10]。

基于细节点邻域的局部描述子具有较强的可解释性，因为每个描述子都可以对应到具体细节点及其周围结构。但这类方法也存在局限。首先，当指纹区域过小或图像质量较差时，可用细节点数量可能不足。其次，细节点检测错误会直接影响描述子构造。再次，在皮肤形变较大时，邻域细节点的相对位置可能发生变化，导致局部匹配不稳定。

### 3.2 SIFT 局部描述子在指纹识别中的应用

SIFT 是 Lowe 提出的经典局部特征方法，最初用于自然图像中的关键点检测和局部描述子构造[13]。SIFT 具有一定的尺度不变性、旋转不变性和光照变化鲁棒性，因此被广泛应用于图像匹配、目标识别和三维重建等任务。由于指纹图像同样存在旋转、平移和局部形变问题，一些研究开始尝试将 SIFT 引入指纹识别。

Park、Pankanti 和 Jain 提出使用 SIFT 特征进行指纹验证，探索了不完全依赖传统细节点检测的局部特征匹配路线[11]。Zhou、Zhong 和 Han 则提出基于 SIFT 的细节点描述子方法，将 SIFT 描述子与细节点邻域结合，并使用改进的全描述子对匹配策略提高指纹识别性能[12]。Bakheet 和 Al-Hamadi 也基于改进 SIFT 特征进行指纹细节点提取和匹配，说明 SIFT 思想仍然能够为指纹局部特征设计提供参考[30]。

然而，SIFT 直接迁移到指纹识别任务中也存在明显问题。第一，指纹图像纹理具有强重复性，不同区域可能呈现相似的脊线方向和纹理结构，这会增加误匹配风险。第二，小面积指纹中可用关键点较少，SIFT 关键点在不同采集图像之间未必稳定。第三，SIFT 原本面向自然图像设计，其梯度直方图结构未必完全适合指纹脊线纹理。因此，SIFT 更适合作为局部描述子构造思想的参考，而不是直接作为复杂指纹识别任务中的最终解决方案。

### 3.3 传统局部描述子的优势与不足

传统局部描述子方法的主要优势在于结构清晰、计算过程可解释、对训练数据依赖较少。与深度学习方法相比，传统方法通常不需要大规模标注数据，适合在数据量有限的场景中使用。此外，基于细节点的局部描述子能够较好地保留人工鉴定中的局部对应关系，便于后续人工复核。

但是，传统方法也受到人工特征设计能力的限制。指纹图像中的噪声、形变、局部缺失和纹理重复会显著影响特征稳定性。当图像质量较差或有效区域较小时，传统方法往往难以构造足够可靠的局部匹配关系。因此，如何在保留细节点可解释性的基础上提高局部描述子的判别能力，成为后续研究的重要方向。

## 4 深度学习在指纹识别中的应用

### 4.1 深度学习用于细节点提取

深度学习方法能够从数据中自动学习图像特征，减少人工设计特征的限制。在指纹识别中，卷积神经网络被用于方向场估计、指纹增强、细节点检测和质量评估等任务。Nguyen、Cao 和 Jain 提出的 MinutiaeNet 是深度学习细节点提取方向的代表方法之一[14-15]。该方法将网络结构与指纹领域知识结合，先通过 CoarseNet（粗检测网络）估计细节点候选区域和方向，再使用 FineNet（精修网络）对候选细节点进行精细判断。与传统细化和交叉数方法相比，MinutiaeNet 对低质量指纹具有更强的鲁棒性。

针对非接触式指纹识别，Zhang 等提出多任务全卷积神经网络（Fully Convolutional Neural Network，全卷积神经网络），用于从灰度非接触式指纹图像中提取细节点[16]。该类研究说明，深度学习方法不仅可以应用于传统接触式指纹，也可以扩展到成像条件更加复杂的非接触式采集场景。

不过，深度学习细节点提取方法也面临数据标注问题。高质量细节点标注需要专业人员完成，成本较高。不同数据集之间的采集设备、图像质量和标注标准也存在差异，这会影响模型泛化能力。

### 4.2 深度学习用于固定长度指纹表示

传统细节点模板通常是变长结构，不同图像中细节点数量不同，这给快速检索、模板保护和大规模比对带来一定困难。DeepPrint 提出学习固定长度指纹表示，将指纹图像压缩为紧凑的深度特征向量[17]。该方法结合了指纹领域知识和深度特征学习思想，使指纹模板更加适合向量检索和快速匹配。

固定长度深度表示的优势在于便于存储、加密和大规模检索。Rohwedder 等对不同嵌入维度和不同传感器类型下的固定长度指纹表示进行了基准测试，说明固定长度表示在跨设备和嵌入尺寸选择方面仍需要进一步研究[31]。Godbole 等提出学习深度指纹表示集成，进一步说明多种深度特征融合可能提升指纹匹配表现[29]。

然而，固定长度表示也存在可解释性不足的问题。细节点模板可以直观显示哪些细节点参与了匹配，而深度向量通常难以解释具体匹配依据。在刑侦鉴定等高可信场景中，系统不仅需要给出匹配分数，还需要提供可复核的局部对应关系。因此，固定长度深度表示更适合作为快速检索或辅助匹配工具，而不宜完全替代可解释的细节点匹配。

### 4.3 深度局部图块描述子

与整图级深度表示不同，深度局部图块描述子重点学习局部区域的特征表达。其基本思路是以细节点、SIFT 关键点或规则网格点为中心，裁剪固定大小的局部图块，再使用卷积神经网络或孪生网络学习描述子，使同一手指对应区域在特征空间中距离更近，不同手指区域距离更远。

MinNet 是该方向的代表工作之一。Ozturk 等提出细节点图块嵌入网络，将细节点周围局部图块映射到嵌入空间，用于自动潜指纹识别[18]。潜指纹通常面积小、质量低、背景噪声多，因此局部图块描述子能够补充传统细节点匹配中的局部纹理信息。对于小面积指纹和残缺指纹而言，这类方法具有较大研究价值。

深度局部描述子的优势在于能够学习更适合指纹纹理的判别性表示，而不是完全依赖人工设计的梯度或几何特征。同时，它仍然可以保留一定局部对应关系，便于与传统几何验证结合。但是，该路线对正负样本构造、图块对齐、训练批次采样和锚点稳定性要求较高。如果正样本对存在错误，或者一个训练批次中存在大量假负样本，模型学习效果可能受到明显影响。

## 5 小面积指纹与残缺指纹识别中的关键问题

### 5.1 小面积指纹的特征不足问题

小面积指纹通常只包含部分脊线区域，可能缺少核心点、三角点和足够数量的细节点。Jea 和 Govindaraju 针对部分指纹识别系统进行了研究，指出部分指纹识别需要在有限局部区域内建立稳定匹配关系[21]。对于这类场景，传统整图匹配方法难以发挥作用，因为可用于全局对齐的信息不足。

局部特征描述子为小面积指纹识别提供了可行思路。系统可以在局部区域中寻找稳定锚点，并围绕锚点提取描述子。如果对应局部区域能够被正确匹配，再结合几何一致性验证，就有可能在较少信息条件下完成身份判断。

### 5.2 锚点稳定性问题

局部描述子通常依赖稳定锚点。锚点可以来自细节点、SIFT 关键点、规则网格采样点或其他显著点。对于完整高质量指纹，细节点相对稳定；但在小面积、低质量或旋转变形明显的指纹中，锚点可能不一致。如果两张来自同一手指的图像在重叠区域中提取不到相同或相近锚点，即使后续描述子具有较强判别能力，也很难建立正确匹配。

因此，局部指纹描述子研究不能只关注神经网络结构，还必须关注锚点检测和图块对齐方法。对于基于图块的深度描述子而言，中心点位置、主方向对齐和图块尺寸都会影响最终特征表达。如果图块方向不一致，模型需要额外学习旋转不变性；如果图块过小，包含的信息不足；如果图块过大，又可能引入过多背景噪声或形变干扰。

### 5.3 指纹纹理重复导致误匹配

指纹纹理由连续脊线构成，局部区域之间具有较强重复性。许多局部图块在视觉上可能非常相似，尤其是在只包含平行脊线、缺少明显细节点的区域中。若描述子只关注小范围纹理，很容易将不同位置甚至不同手指的相似区域误判为匹配。

因此，局部描述子通常需要结合多种约束。第一，可以引入中心细节点方向、邻域细节点结构和局部方向场信息。第二，可以使用全局几何验证方法，例如 RANSAC（Random Sample Consensus，随机采样一致性）思想，对候选匹配关系进行一致性筛选。第三，可以将多个局部匹配结果组合起来，而不是依赖单个局部图块的相似度判断身份。

### 5.4 样本构造与训练策略问题

深度局部描述子训练依赖正负样本对。正样本通常表示来自同一手指且对应同一局部区域的图块，负样本则来自不同手指或不同区域。实际构造中，正样本标注并不简单。若两张指纹存在形变或采集角度差异，需要通过特征匹配、人工标注或几何变换估计确定局部对应关系。错误正样本会使模型学习到错误相似性。

批次采样策略也会影响模型训练效果。如果一个训练批次中包含来自同一手指但不同位置的多个图块，这些图块在损失函数中可能被当作负样本，从而形成假负样本问题。对于 HardNet（困难样本描述子网络）或三元组损失等度量学习方法，困难负样本选择会直接影响收敛效果和最终判别能力。因此，局部指纹描述子训练不仅是网络结构问题，也是数据组织和采样策略问题。

## 6 当前研究挑战

### 6.1 数据集与标注不足

深度学习方法通常需要大量高质量训练数据，而指纹数据具有隐私敏感性，公开数据集规模相对有限。虽然 FVC 系列数据集和部分 NIST 数据集为研究提供了基础，但对于深度局部描述子训练而言，仍然缺少大规模、细粒度、带局部对应标注的数据集。Cao 和 Jain 对自动潜指纹识别的研究也表明，潜指纹场景中存在质量差、背景复杂和人工标注困难等问题[19]。

### 6.2 模型泛化能力不足

指纹采集设备、分辨率、图像质量和成像方式存在明显差异。一个模型在某一设备或某一数据集上表现较好，不代表能够泛化到其他设备或真实业务场景。固定长度指纹表示在跨传感器场景下的表现差异，也说明深度模型需要更强的跨域泛化能力[31]。

### 6.3 可解释性不足

传统细节点匹配可以展示细节点对应关系，因此具有较强可解释性。深度学习方法虽然可能提高识别性能，但其内部特征难以直接解释。在司法鉴定和高安全身份认证场景中，仅给出深度特征相似度是不够的。系统还需要解释哪些区域、哪些细节点或哪些局部图块支持匹配判断。因此，未来深度方法需要与可视化、局部对应关系展示和人工复核机制结合。

### 6.4 安全与隐私问题

指纹属于敏感生物特征，一旦泄露很难像密码一样更换。Cao 和 Jain 关于从细节点重建指纹图像的研究说明，指纹模板保护是不可忽视的问题[26]。Bontrager 等提出 DeepMasterPrints（深度万能指纹）攻击，说明深度学习技术也可能被用于生成具有攻击性的指纹模式[27]。因此，指纹识别研究不仅要关注准确率，还需要关注模板加密、攻击防御和隐私保护。

## 7 未来发展趋势

### 7.1 细节点锚定与深度图块描述子融合

未来指纹识别方法很可能不会完全抛弃细节点，而是将细节点作为稳定锚点，再结合深度局部图块描述子增强判别能力。这种路线既保留细节点的可解释性，又利用深度学习提升局部纹理表达能力。对于小面积和残缺指纹，细节点锚定的深度图块描述子尤其具有研究价值。

### 7.2 多尺度局部特征融合

单一尺度的局部图块难以同时兼顾细节纹理和邻域结构。未来方法可以采用多尺度图块，例如小尺度图块关注脊线细节，大尺度图块关注邻域方向场和细节点布局。多尺度融合能够缓解图块过小信息不足和图块过大噪声过多的问题。

### 7.3 小面积指纹专用模型

随着移动终端、嵌入式设备和非接触式采集的发展，系统经常只能获得部分指纹区域。因此，小面积指纹识别应成为独立研究方向。未来可以针对小面积图像设计专门的锚点检测、图块描述子、匹配评分和几何验证方法，而不是简单套用完整指纹识别流程。

### 7.4 可解释深度匹配

深度学习方法要在高可信场景中应用，需要解决可解释性问题。未来系统应能够输出匹配分数、局部图块对应关系、细节点匹配对、置信度和可视化证据。这样既可以提高用户信任，也便于人工专家复核。

### 7.5 模板保护与安全识别

未来指纹识别系统需要同时考虑识别性能和模板安全。固定长度深度表示虽然便于检索和加密，但仍需研究其可逆性、攻击风险和隐私保护机制。安全指纹识别系统应在特征提取、模板存储、匹配计算和通信传输等环节建立完整保护机制。

------

## 8 结论

本文围绕基于局部特征描述子的指纹识别方法进行了综述。传统指纹识别方法主要依赖细节点特征，其优点是表示紧凑、可解释性强、工程应用成熟，但在低质量、小面积和残缺指纹场景下容易受到图像质量、细节点数量和局部形变的影响。SIFT 等传统局部描述子方法为指纹识别提供了新的局部匹配思路，但由于指纹纹理具有强重复性，直接迁移自然图像描述子仍然存在误匹配风险。

深度学习方法为指纹识别提供了新的技术路径。MinutiaeNet 等方法提高了细节点提取的鲁棒性，DeepPrint 等方法探索了固定长度指纹表示，MinNet 等方法则说明局部图块深度描述子在潜指纹和残缺指纹识别中具有潜力。总体来看，未来指纹识别方法不应在传统细节点方法和深度学习方法之间二选一，而应采用混合式框架，将细节点的可解释性、局部图像描述子的判别能力和深度学习的特征表达能力结合起来。

对于小面积指纹识别任务，较合理的技术路线是：首先提取稳定锚点，例如细节点或关键点；然后围绕锚点裁剪统一尺度和方向的局部图块；再使用深度网络学习局部描述子；最后结合全局几何验证和多局部匹配结果进行身份判断。该路线既符合指纹识别领域长期积累的细节点理论，也能够吸收深度学习在特征表达方面的优势。未来研究应进一步关注数据集构建、正负样本标注、批次采样策略、跨设备泛化能力、可解释匹配和模板安全等问题。

## 参考文献

[1] MALTONI D, MAIO D, JAIN A K, et al. Handbook of fingerprint recognition[M]. 2nd ed. London: Springer, 2009.

[2] HONG L, WAN Y, JAIN A. Fingerprint image enhancement: algorithm and performance evaluation[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 1998, 20(8): 777-789.

[3] JAIN A K, HONG L, BOLLE R. On-line fingerprint verification[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 1997, 19(4): 302-314.

[4] JAIN A K, PRABHAKAR S, HONG L, et al. Filterbank-based fingerprint matching[J]. IEEE Transactions on Image Processing, 2000, 9(5): 846-859.

[5] MAIO D, MALTONI D, CAPPELLI R, et al. FVC2000: fingerprint verification competition[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2002, 24(3): 402-412.

[6] MAIO D, MALTONI D, CAPPELLI R, et al. FVC2002: second fingerprint verification competition[C]//Proceedings of the 16th International Conference on Pattern Recognition. Quebec City: IEEE, 2002: 811-814.

[7] MAIO D, MALTONI D, CAPPELLI R, et al. FVC2004: third fingerprint verification competition[C]//Proceedings of the International Conference on Biometric Authentication. Berlin: Springer, 2004: 1-7.

[8] CAPPELLI R, MAIO D, MALTONI D, et al. Performance evaluation of fingerprint verification systems[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2006, 28(1): 3-18.

[9] PERALTA D, GALAR M, TRIGUERO I, et al. A survey on fingerprint minutiae-based local matching for verification and identification: taxonomy and experimental evaluation[J]. Information Sciences, 2015, 315: 67-87.

[10] FENG J, ZHOU J. A performance evaluation of fingerprint minutia descriptors[C]//Proceedings of the International Conference on Hand-Based Biometrics. Hong Kong: IEEE, 2011: 1-6.

[11] PARK U, PANKANTI S, JAIN A K. Fingerprint verification using SIFT features[C]//Proceedings of SPIE Defense and Security Symposium. Orlando: SPIE, 2008.

[12] ZHOU R, ZHONG D, HAN J. Fingerprint identification using SIFT-based minutia descriptors and improved all descriptor-pair matching[J]. Sensors, 2013, 13(3): 3142-3156.

[13] LOWE D G. Distinctive image features from scale-invariant keypoints[J]. International Journal of Computer Vision, 2004, 60(2): 91-110.

[14] NGUYEN D L, CAO K, JAIN A K. Robust minutiae extractor: integrating deep networks and fingerprint domain knowledge[C]//Proceedings of the 11th IAPR International Conference on Biometrics. Gold Coast: IEEE, 2018: 9-16.

[15] NGUYEN D L, CAO K, JAIN A K. MinutiaeNet: a robust minutiae extractor for fingerprint recognition[EB/OL]. arXiv:1712.09401, 2017.

[16] ZHANG Z, WANG S, LIU J, et al. A multi-task fully deep convolutional neural network for minutiae extraction from contactless fingerprints[J]. Sensors, 2022, 22(23): 9255.

[17] ENGELSMA J J, CAO K, JAIN A K. Learning a fixed-length fingerprint representation[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2021, 43(6): 1981-1997.

[18] OZTURK H I, ENGELSMA J J, CAO K, et al. MinNet: minutia patch embedding network for automated latent fingerprint recognition[C]//Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops. New Orleans: IEEE, 2022: 1627-1635.

[19] CAO K, JAIN A K. Automated latent fingerprint recognition[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2019, 41(4): 788-800.

[20] YOON S, FENG J, JAIN A K. Latent fingerprint enhancement via robust orientation field estimation[C]//Proceedings of the International Joint Conference on Biometrics. Washington, DC: IEEE, 2011: 1-8.

[21] JEA T Y, GOVINDARAJU V. A minutia-based partial fingerprint recognition system[J]. Pattern Recognition, 2005, 38(10): 1672-1684.

[22] CHEN X, TIAN J, YANG X. A new algorithm for distorted fingerprints matching based on normalized fuzzy similarity measure[J]. IEEE Transactions on Image Processing, 2006, 15(3): 767-776.

[23] ROSS A, DASS S, JAIN A K. A deformable model for fingerprint matching[J]. Pattern Recognition, 2005, 38(1): 95-103.

[24] YANG J, LIU L, JIANG T, et al. A modified Gabor filter design method for fingerprint image enhancement[J]. Pattern Recognition Letters, 2003, 24(12): 1805-1817.

[25] ZHAO Q, ZHANG D, ZHANG L, et al. A generative model for fingerprint minutiae[C]//Proceedings of the International Conference on Biometrics. New Delhi: IEEE, 2012: 1-6.

[26] CAO K, JAIN A K. Learning fingerprint reconstruction: from minutiae to image[J]. IEEE Transactions on Information Forensics and Security, 2015, 10(1): 104-117.

[27] BONTRAGER P, ROY A, TOGELIUS J, et al. DeepMasterPrints: generating masterprints for dictionary attacks via latent variable evolution[C]//Proceedings of the IEEE 9th International Conference on Biometrics Theory, Applications and Systems. Redondo Beach: IEEE, 2018: 1-9.

[28] CHOWDHURY A, FERRARA M, FRONTHALER H, et al. Can a CNN automatically learn the significance of minutiae points for fingerprint matching?[C]//Proceedings of the IEEE Winter Conference on Applications of Computer Vision. Snowmass Village: IEEE, 2020: 1439-1448.

[29] GODBOLE A, ENGELSMA J J, CAO K, et al. Learning an ensemble of deep fingerprint representations[EB/OL]. arXiv preprint, 2022.

[30] BAKHEET S, AL-HAMADI A. Robust fingerprint minutiae extraction and matching based on improved SIFT features[J]. Applied Sciences, 2022, 12(12): 6125.

[31] ROHWEDDER T, OSORIO-ROIG D, RATHGEB C, et al. Benchmarking fixed-length fingerprint representations across different embedding sizes and sensor types[C]//Proceedings of the International Conference of the Biometrics Special Interest Group. Darmstadt: Gesellschaft für Informatik, 2023.

[32] YANG L. Advancements in fingerprint recognition through deep learning: a comprehensive analysis of novel algorithms[J]. Applied and Computational Engineering, 2024, 37: 70-76.