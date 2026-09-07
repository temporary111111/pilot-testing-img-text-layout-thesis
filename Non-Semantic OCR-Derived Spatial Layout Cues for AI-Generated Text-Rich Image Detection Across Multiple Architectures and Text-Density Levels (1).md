

**CS 124 \- THESIS 1**

# **THESIS TOPIC PROPOSAL**

#  **OCR-Derived Spatial Layout Cues for AI-Generated Text-Rich Image Detection Across Multiple Architectures and Text-Density Levels** 

Babila, Angeline Borigas, Bryan Real, Daniel Mark

# **I. Proposed Title**

**OCR-Derived Spatial Layout Cues for AI-Generated Text-Rich Image Detection Across Multiple Architectures and Text-Density Levels** 

| Criterion | Proposed Study |
| :---- | ----- |
| **CS Domain** | Artificial Perception (Computer Vision), with Machine Learning and Artificial Intelligence |
| **Computing Contribution** | Controlled comparison of visual-only, layout-only, and combined visual-layout models across selected architectures to determine whether OCR-derived spatial layout information provides useful additional information for detecting AI-generated text-rich images.  |
| **BU Agenda** | Global Competitiveness of Business and Industry – supporting trustworthy digital transformation and responsible use of AI-generated visual content |
| **SDG** | Primary: SDG 9 – Industry, Innovation and Infrastructure; Secondary relevance: SDG 16 – Peace, Justice and Strong Institutions |
|  **Beneficiary** | Researchers, digital-content verification personnel, educators, and organizations that handle text-rich digital artifacts such as receipts, posters, tables, and interface screenshots |
|  **Expected Innovation** | A controlled study of OCR-derived spatial layout cues, without using recognized text or its meaning, to determine whether they provide useful additional information for AI-generated text-rich image detection across selected architectures and text-density levels.  |

# **Background**

	AI image generators have improved over time and are now able to create more than just artistic scenery or images. They can now generate images that contain readable text and organized content such as posters, receipts, charts, academic materials, and user-interface screenshots. Although generative AI may be useful in many areas, it also makes it harder to detect whether the content is real or AI-generated. This is important because people often use text-rich images as sources of information, records, and supporting materials. Wang et al. (2026) identified this as a content-authenticity problem and examined several types of AI-generated text-rich images, including commercial posters, infographic charts, academic posters, receipts, tables, and user-interface screenshots. 

Detecting AI-generated images is already a known research problem in Computer Vision. Studies such as GenImage have provided large datasets for evaluating different detection methods. Later research showed that good performance on one dataset does not always mean that a detector will work equally well on new image generators or different image conditions (Zhu et al., 2023; Li et al., 2025). Text-rich images make this problem more challenging because their appearance depends not only on objects, colors, and textures, but also on how text is arranged on the page. Wang et al. (2026) reported that some text-rich image categories, especially highly structured ones such as tables, were difficult for several existing detectors. Zhang et al. (2026) also found that the performance of many detection methods decreased as the amount of visible text increased, which they described as the “Text Density Curse.” 

Position and arrangement of text regions in a text-rich image can provide useful information for detection. Optical Character Recognition, or OCR, is commonly used to find text in an image. In this study, OCR will not be used to understand the words themselves but instead it will be used only to identify where the text appears in the image. Previous research has shown that the positions and spatial relationships of detected text can provide useful information in document analysis. For example, Joren et al. (2020) used OCR-based location information to help detect manipulated business documents, while Qu et al. (2026) used OCR information in detecting tampered text. These studies show that text location and arrangement may provide useful evidence for detection, but their focus was document manipulation or tampering rather than the detection of fully AI-generated text-rich images. 

A specific research question remains about whether simple page-level text-layout information can help in detecting AI-generated text-rich images. Existing studies have examined general AI-generated image detection, text-rich image detection, OCR-based document analysis, and text quality. However, the reviewed literature did not directly evaluate the same combination proposed in this study: visual information, OCR-based spatial layout information, and their combination for detecting fully AI-generated text-rich images, together with analysis across different text-density levels. This is a limited observation based on the literature reviewed for this study and does not mean that OCR, layout analysis, or the combination of visual and text-related information is new. 

To examine this question, the study will compare three approaches: visual-only detection, layout-only detection, and a combined visual-layout approach. The study will use multiple selected architectures to determine whether the contribution of layout information is consistent or changes depending on the model used. The OCR component will use only the positions and arrangement of detected text regions and will not use the recognized words or their meanings. The study will also examine whether detection performance changes depending on how much of the image is covered by text. Text density will be used for analysis rather than as a separate input to the model. All approaches will be evaluated using the same dataset divisions and evaluation procedure to allow a fair comparison. Positive, mixed, or negative results will all be treated as valid findings. 

The main contribution of the study is a controlled evaluation of whether OCR-based text-layout information provides useful additional information for detecting AI-generated text-rich images across the selected architectures and different text-density levels. The study will use lightweight architectures to keep the experiments practical while allowing the results to be compared across different models. It is mainly aligned with SDG 9: Industry, Innovation and Infrastructure because it explores an approach that may contribute to accessible and efficient digital-content verification technologies. It also has relevance to SDG 16: Peace, Justice and Strong Institutions because research on detecting synthetic visual content can support information integrity and digital verification. However, the study does not claim to solve misinformation, fraud, or digital verification as a whole. Its focus is limited to determining whether the spatial arrangement of detected text regions provides useful additional information when distinguishing real and AI-generated text-rich images. 

# **Introduction of Proposed System**

The proposed study will use an experimental framework for detecting AI-generated text-rich images by evaluating two sources of information: the visual appearance of the image and the spatial arrangement of OCR-detected text regions. The main purpose of the framework is to determine whether OCR-derived spatial layout information can provide useful additional information for distinguishing real and AI-generated text-rich images. OCR will be used only to identify the positions of text regions, while recognized words and their meaning will not be included in the classification process.

The study will compare three main approaches: visual-only, layout-only, and visual-layout fusion. The visual-only approach will learn from the image pixels, while the layout-only approach will use spatial information obtained from OCR-detected text regions. These layout representations will include page-level geometric features and a normalized binary spatial-layout map. The visual-layout fusion approach will combine learned visual features with the OCR-derived layout representation before classification. This comparison will allow the study to examine what each source of information contributes separately and whether combining them changes detection performance.

Instead of relying on only one visual architecture, the study will evaluate three selected architectures for the visual-based configurations. This will allow the usefulness of the proposed layout cues to be examined without depending on the behavior of a single architecture. The exact implementation of the layout-only configurations in relation to these architectures will be defined separately as part of the final experimental design, since the layout approach uses geometric features and spatial-layout representations rather than the original image pixels.

The experimental process will begin with the controlled TextRich dataset and a consistent image preprocessing procedure. OCR text detection will then locate the text regions in each image, after which their coordinates will be converted into the required spatial-layout representations. These representations will be used according to the visual-only, layout-only, and visual-layout fusion approaches. All configurations will follow the same fixed data partitions and evaluation protocol so that their results can be compared under consistent conditions.

The performance result will be analyzed overall and across low, medium, and high text-density levels. Text density will be used only for analysis and will not be provided directly to the models as an additional input. Through these comparisons, the study will determine whether OCR-derived spatial layout cues contain useful discriminatory information on their own, provide complementary information when combined with visual features, or provide little or no additional benefit. Any of these outcomes will be treated as a valid finding of the study.

# **General Objective**

The primary goal of this study is to develop and evaluate different model configurations across selected architectures to determine whether OCR-derived spatial layout information provides useful additional information for detecting AI-generated text-rich images across different text-density levels. 

# **Specific Objectives**

1. To prepare the experimental inputs needed for the study by obtaining the OCR-detected text regions from the TextRich images and using their positions to create the spatial layout representations required for the layout-only and combined visual-layout approaches; 

2. To implement the visual-only, layout-only, and combined visual-layout approaches using the selected architectures while excluding recognized text and its meaning from the OCR-based layout input; 

3. To evaluate and compare the implemented models using accuracy, precision, recall, F1-score, macro-F1, and ROC-AUC, and to analyze their performance across image categories and low, medium, and high text-density levels; and 

4. To determine, based on the evaluation results, whether OCR-derived spatial layout information provides useful additional information for detecting AI-generated text-rich images across the selected architectures and text-density levels. 

# 

# **Scope and Limitations**

1. ## **Dataset Scope**

The study will use the TextRich benchmark, which contains real and AI-generated text-rich images from six categories: academic posters, commercial posters, infographic charts, receipts, tables, and user-interface screenshots. The study will focus only on these image categories and will treat the detection task as a binary classification problem between real and AI-generated images.  
The experimental data will be divided into separate training, validation, and test sets. The same data divisions will be used across the different model configurations to allow a fair comparison. The test set will only be used for the final evaluation and will not be used when making decisions about the models.

2. ## **Algorithm and Model Scope**

The study will evaluate three main approaches: visual-only detection, layout-only detection, and combined visual-layout detection. These approaches will be tested using selected architectures so that the study can examine whether the contribution of layout information is consistent or changes depending on the model used.  
For the layout-based approaches, OCR will be used only to locate text regions in the image. The positions and arrangement of these regions will be used to create spatial layout representations. Recognized words, their meaning, and other semantic text information will not be included as part of the layout input.  
The study will focus only on the selected model architectures and OCR-derived spatial layout representations. Large vision-language models, text-language features, model ensembles, and extensive searches for additional architectures are outside the scope of the study.  
Text density will also be considered as part of the analysis. Images will be grouped into low, medium, and high text-density levels based on the amount of image area occupied by detected text. Text density will be used to examine model performance and will not be provided as a separate input to the classifiers.

3. ## **System Scope**

The study will evaluate and compare the implemented models using standard classification measures such as accuracy, precision, recall, F1-score, macro-F1, and ROC-AUC. Results will be examined overall and across the available image categories and text-density levels.  
The evaluation will focus on determining whether OCR-derived spatial layout information provides useful additional information compared with using visual information alone. The study will also examine whether this effect remains similar or changes across the selected architectures and text-density levels.  
The study will not assume that the combined visual-layout approach must perform better. Positive, mixed, or negative results will all be considered valid findings when drawing the conclusion of the study.

4. ## **Evaluation Scope**

The study will include a research prototype that demonstrates the selected detection process. Its purpose will be limited to accepting a text-rich image, processing it through the selected model, and presenting the predicted classification result. OCR-based layout information may also be displayed for explanation or diagnostic purposes.  
The prototype is intended only as a demonstration of the research and will not be developed as a production-ready forensic system. Features such as user accounts, cloud-scale processing, mobile deployment, integration with external platforms, advanced security mechanisms, and large-scale real-time monitoring are outside the scope of the study.

5. ## **Limitations of the Study**

The study is limited to the TextRich benchmark and the image categories included in the selected experimental data. Therefore, the results will describe the performance of the proposed approaches within this experimental setting and should not be treated as universal performance for all types of text-rich images.

The AI-generated images in TextRich are produced using the generator represented by the benchmark. Because of this, the study cannot claim that the same results will apply to images produced by all current or future AI image generators.

The spatial layout information depends on the performance of the selected OCR system. OCR may fail to detect some text, incorrectly locate text regions, or separate and combine regions differently from their actual appearance. These errors may affect the layout information provided to the models.

The study intentionally excludes recognized words and their meaning. It therefore does not examine whether spelling errors, word choice, sentence meaning, or other text-based information can help determine whether an image is real or AI-generated.

The layout representation will focus on the position and arrangement of detected text regions. Other properties such as font style, typography, reading order, semantic document sections, and more complex relationships between text regions are outside the scope of the study.

The study will not evaluate every possible image condition found in real-world use. Its results cannot automatically be generalized to unseen AI generators, heavily edited images, social-media recompression, adversarial manipulation, or other deployment environments that are not represented in the experimental data.

Finally, the developed models and research prototype are intended for experimental evaluation only. Their predictions will not be treated as legal, forensic, or definitive proof that an image is real or AI-generated.

# **References**

Chivaran, N., & Ni, J. (2025). LAID: Lightweight AI-generated image detection in spatial and spectral domains. arXiv:2507.05162. [https://doi.org/10.48550/arXiv.2507.05162](https://doi.org/10.48550/arXiv.2507.05162)

Howard, A., Sandler, M., Chu, G., Chen, L.-C., Chen, B., Tan, M., Wang, W., Zhu, Y., Pang, R., Vasudevan, V., Le, Q. V., & Adam, H. (2019). Searching for MobileNetV3. Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), 1314–1324. [https://doi.org/10.1109/ICCV.2019.00140](https://doi.org/10.1109/ICCV.2019.00140)

Joren, H., Gupta, O., & Raviv, D. (2020). OCR graph features for manipulation detection in documents. arXiv:2009.05158. [https://doi.org/10.48550/arXiv.2009.05158](https://doi.org/10.48550/arXiv.2009.05158)

Koltsov, K., Gushchin, A., Vatolin, D., & Antsiferova, A. (2026). TIQA: Human-aligned perceptual text quality assessment in generated images. arXiv:2603.07119. [https://doi.org/10.48550/arXiv.2603.07119](https://doi.org/10.48550/arXiv.2603.07119)

Li, Z., Yan, J., He, Z., Zeng, K., Jiang, W., Xiong, L., & Fu, Z. (2025). Is artificial intelligence generated image detection a solved problem? arXiv:2505.12335. Accepted to the NeurIPS 2025 Datasets and Benchmarks Track. [https://doi.org/10.48550/arXiv.2505.12335](https://doi.org/10.48550/arXiv.2505.12335)

Ma, N., Zhang, X., Zheng, H.-T., & Sun, J. (2018). ShuffleNet V2: Practical guidelines for efficient CNN architecture design. Proceedings of the European Conference on Computer Vision (ECCV). [https://doi.org/10.1007/978-3-030-01264-9\_8](https://doi.org/10.1007/978-3-030-01264-9_8)

Maaz, M., Shaker, A., Cholakkal, H., Khan, S., Zamir, S. W., Anwer, R. M., & Shahbaz Khan, F. (2023). EdgeNeXt: Efficiently amalgamated CNN-Transformer architecture for mobile vision applications. In Computer Vision – ECCV 2022 Workshops: Tel Aviv, Israel, October 23–27, 2022, Proceedings, Part VII (pp. 3–20). Springer. [https://doi.org/10.1007/978-3-031-25082-8\_1](https://doi.org/10.1007/978-3-031-25082-8_1)

Qu, C., Zhong, Y., Liu, J., Zhu, X., Yu, B., & Jin, L. (2026). TextShield-R1: Reinforced reasoning for tampered text detection. arXiv:2602.19828. [https://doi.org/10.48550/arXiv.2602.19828](https://doi.org/10.48550/arXiv.2602.19828)

Wang, Y., Wang, S., Zhang, W., & Ouyang, Y. (2026). TextRich: A multi-domain benchmark for detecting AI-generated text-rich images from GPT-Image-2. arXiv:2606.19259. [https://doi.org/10.48550/arXiv.2606.19259](https://doi.org/10.48550/arXiv.2606.19259)

Zhang, Y., Miao, C., Liao, M., Liu, T., Wang, X., Gong, T., Chu, Q., & Yu, N. (2026). TextFake: Benchmarking AI-generated image detection on text-rich images. arXiv:2606.01050. [https://doi.org/10.48550/arXiv.2606.01050](https://doi.org/10.48550/arXiv.2606.01050)

Zhu, M., Chen, H., Yan, Q., Huang, X., Lin, G., Li, W., Tu, Z., Hu, H., Hu, J., & Wang, Y. (2023). GenImage: A million-scale benchmark for detecting AI-generated image. Advances in Neural Information Processing Systems, 36, 77771–77782.

