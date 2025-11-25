# Reproducibility & Extension Study of *Binoculars*: Zero-Shot Detection of LLM-Generated Text

This repository contains the implementation and analysis for the **reproducibility study** of  
*“Spotting LLMs With Binoculars: Zero-Shot Detection of Machine-Generated Text” (Hans et al., 2024)*  
and an **extension experiment in a low-resource language (Haitian Creole).**

<p align="center">
  <img src="./assets/binoculars.jpg" width="300" height="300" alt="Binoculars concept illustration">
</p>

---

## Project Overview

**Objectives**

- Reproduce results from the original Binoculars paper on **CC-News, CNN, and PubMed** datasets.

- Evaluate model detection performance using **Falcon-7B base & Falcon-7B-Instruct**.

- Extend the zero-shot evaluation to **Haitian Creole**, a low-resource language.

- Compare **prompted vs. non-prompted generation strategies** using *Aya 101* and *GPT-4*.

- Analyze cross-model performance using **Falcon H1 (multilingual)** as an additional detection pair.

---

## Experimental Setup

| Component | Configuration |
|----------|----------------|
| **Model Pairs (Detector)** | Falcon-7B (observer) + Falcon-7B-Instruct (performer)<br>Falcon-H1 1.5B base + H1 deep (extension only) |
| **Generators** | Aya 101 & GPT-4 |
| **Generation Methods** | • *Prompted*: explicitly asked to write in Haitian Creole<br>• *Non-prompted*: continuation on raw text |
| **Chunking** | ~4000 characters per sample, cut only after final word (~5200 chunks) |
| **Text Types** | News, poetry, blogs/Reddit posts |
| **Evaluation Metrics** | AUC, F1, TPR@FPR=0.01, Best Threshold |

---

## Summary of Findings

| Task | Key Takeaway |
|------|--------------|
| **Reproducibility (English)** | Successfully recovered strong performance trends, though slightly lower than paper (likely due to token limit & hardware constraints). |
| **Extension (Haitian Creole)** | • Non-prompted text resulted in significantly better performance.<br>• Prompted generation did not improved quality. |
| **Overall** | Model performance drops dramatically in low-resource language settings. Perhaps aligned multilingual detection models might improve performance. |

---

## Repository Structure

| Folders | Details |
|----------|----------------|
| **notebooks** | Google Colab notebook (code) |
| **results** | Results folders for metrics reports per run |
| **slides** | PPT presentation file |
| **extensions** | Links, texts, raw chunked jsonl files (pre generated texts), links of raw data|
| **datasets** | hk_news, hk_essays, hk_blogs subfolders with gpt4 and aya101 generated texts |


---

## Usage

Clone the repository and open either notebook in Google Colab or local Jupyter:

```bash
git clone <repo-url>
```
notebooks/binoculars_reproducibility.ipynb

GPU is recommended due to model size. Tested on A100.

---

## Limitations

All results are zero-shot and may degrade significantly in low-resource contexts.

Even with prompting, detectors tend to over-classify human-written Creole as machine-generated.

English-only base models struggle without multilingual alignment.

## How to Reference

```
bibtex
@misc{dorvil2025repro_binoculars,
  title={Reproducibility and Low-Resource Language Extension of Binoculars},
  author={Angeline Dorvil},
  year={2025},
  note={Graduate Course Project, Computer Science}
}
```

Please also cite the original paper:

```
bibtex
@misc{hans2024spotting,
      title={Spotting LLMs With Binoculars: Zero-Shot Detection of Machine-Generated Text}, 
      author={Abhimanyu Hans and Avi Schwarzschild and Valeriia Cherepanova and Hamid Kazemi and Aniruddha Saha and Micah Goldblum and Jonas Geiping and Tom Goldstein},
      year={2024},
      eprint={2401.12070},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

