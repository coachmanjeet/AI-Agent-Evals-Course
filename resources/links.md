# Curated links

Grouped by week. Framework docs first, then one or two seminal reads per theme.

## All weeks

- LangSmith docs (tracing, datasets, annotation, monitoring): https://docs.langchain.com/langsmith

## Week 1 — Foundations

- LangSmith observability concepts (traces, spans, runs): https://docs.langchain.com/langsmith/observability-concepts

## Week 2 — LLM judges

- LangSmith evaluators (custom evaluators, `evaluate()`, experiments): https://docs.langchain.com/langsmith/evaluation

## Week 3 — Adversarial testing

- Promptfoo docs (red teaming, scans, config reference): https://promptfoo.dev

## Week 4 — RAG eval

- Braintrust docs (experiments, scorers, autoevals): https://www.braintrust.dev/docs

## Week 5 — Multi-agent eval

- CrewAI docs (agents, tasks, crews, tools): https://docs.crewai.com

## Week 6 — Production

- GitHub Actions docs (workflows, schedules, secrets): https://docs.github.com/actions

## Maven sessions — "Cracking the AI Evals Interview" (2026-10-06 recap, fwd by Manjeet)

Hamel Husain & Shreya Shankar walk through an evals-interview style assignment using a
fictional tree-care app: handling missing/inconsistent labels, running experiments,
explaining what results mean for the product, plus a report structure for the write-up.
Slides only make sense alongside the recording.

- [Session recording](https://link.courses.maven.com/c/eJw8z8GOqyAUxvGngR0GDhRwweJufA1zhGOlVTFgbe7bT6Yzme0vX_Lln4JJUk03TkG5XmkF1ktOG-Z1jCu2FqZaMEVs56-e_w8K71KfbSkHp_0af_z1yikctaROzj7NsfdikiCFQSsFphSFTvHWu8n7NFm-BAALOPvUO3LgHGnSjlKUhrybezQ8B5BglZRW-ZtSvtOTiW62RlpNziZgRsbyqo1at-FFexfLxnMb51q28SNhwLURX8Nynkdj-h-DgcHwt2YwHAwG6chFx2CIFeMz73dxLiQwC7pwbSLvJ9Ur05vXsOH-IDof-FywMiPv3_Gf4xaXUtYxp9Bra_gV4CsAAP__5JRwlg)
- [Session slides (watch the recording first)](https://link.courses.maven.com/c/eJws0E9r3DAUBPBPI93W6N9q7YMOoUWQQCntoaS5mGc92VZiW66evGn76ctuc_0xA8OgMyjkcObRyUsntVS2FTyukJY-LEDkhpIBA1D90Ppnj-49lzea887jdu3_-3EkdHvJ2IixxTF07WkQSpwMWHECxHDSGM7dZWhbHCyfnYUYBKgR26ARpTLWdEMnlB2NgbMZeHJKKCuFsLI9S9k2ejDhMlojrI4Xi4oZEfJRKFKzwjVuTcgrT9SPJa_9XZyHhSJf3FzrTkw_MOWZ8pgDNVPO0xJvHab8XiLFrUJNebsFmPJyV7_oqX7H0U6Vnl-mrw_0_P7J__7p5y-jeNIbvRzf_j7KH8cjUz5iqkz7g3amP9MMJW0TL26F7TXG-gpvMxRmxHQ76z6Uwpzz0id0nbaGX536FwAA__8Ki4GO)
- [Maven evals guide — starting point for "why" questions](https://link.courses.maven.com/c/eJwsz71yhCAUQOGngU6HPxELijS-hnPhXlZ3cTHgmsnbZ7JJ-zVnDnqDQoaBk5fjJLVU1glOO2x5iRla86EWwAjt_Nfz-yD_VeqjreXg9LyWP3-9NvRHLdiL5DDFyXVBKNEZsKIDxNhpjMM0BucwWL76kABCTEYNI9Ikkxu1GXSQMQkiOQa-eSWUlUJY6QYpXa-DiWOyRlhNo0XFjIjlVRu1foeLnn0sO9_akmrZl7f4GXIjnv16nkdj-oOpmal5hZ1yj3QxNYdcbkzNR2lnY2qmC3LrEnwyNfPqd3jeic47PFaozIjb7-u70-JaSl429JO2hl9e_QQAAP__L1trHg)

Evals-guide deep dives, mapped to course weeks:

- [How does error analysis help you decide what to measure? (Week 1)](https://link.courses.maven.com/c/eJws0MFurSAQxvGn0R0GUFEXLO7G1zADM1ZaEMtwPDlvf9PTbn-ZfzL50A4olRtbsmpaVK-0mWVLCULcfARm60oG9MD1T-vrIvvM5YuPfLV03tuvPx4B7VUydnKfcffLLJzUUgxgpABEL3r04zK5eUZn2sOOkgYCZ6YR9SjBLNrtaAyB6RflZ9MGq6U2Skqj5lGpuevd4KfdDNL0NBnUzSB9fhQm7hLcdHY-pzbwtpectrfYFSJTG-1R68VN_6_Ra6PXAxLFDulu9Opi_mj0emWu3OiVbogsdvh-X_bf4nm8RGBBpeQi4IT44sCCswjpyqXCWUU4RYxJ_KZwojjy86cJVVxU9lwSYVtsgvOTqH7C1wGlGeTHz27vn9kfOcctoF16M7S31f8DAAD__8A7ho8)
- [Why avoid generic metrics like helpfulness? (Week 2)](https://link.courses.maven.com/c/eJws0DGSpSAQxvHTSIaFqIgBwSZew2rodmQGHw6Nbs3tt547Yf_qH3R96AZUnR8FuW6au77TxipBB8S0hgTMzpcMGIDrr9afk9zfXL54z6eg173-9-uK6M6SsVWbxS3MVnqllRzAKAmIQfYYxnny1qI3Ynfewrz5ebKzH42f_Nh7tAN6PY7TFMwootNKm04p09mx62zb-yFMmxmU6WkyqJtBhXwVJm4PuOnVhnyIyOtW8rE-4hZITCK5vdaTm_5Po5dGLzsclFqku9GLT_mj0cuZuXKjF7ohsdzg-yn7b8l7vhLKKC8mWQjwR9b8HO_0ghrzSx5USwwsijvg9UlUP-Frh9IM6uM9zvMYhz3ntEZ0c28GcTv9LwAA__8CnHyZ)
- [Why use specific pass/fail checks instead of 1-to-5 ratings? (Week 2)](https://link.courses.maven.com/c/eJws0LGSozAQBNCvgWxckgAhAgWX8BuuQTMYrQViNTJb_vur9V36qjvoJt-T0svQstfjpDttrFMt7xjTPSQU8UvJSAGl_tf6Ptn_5PKULZ8tH9f9n79ekfxZMt3U6mgNk4NFGQU9WgVIFKCjMEzj4hwttt28Hd3oFE3DyqEbiAajLdnAgRyN64Rt9EYZq5Wy2g1au1u39GFcba9sx6Ml0_Qq5FcRltuOFx-3kPc2yn0teb9_xM-YhNvkt1pPabo_jZkbM2-4c7oRX42Zl5QfjZnPLFUaM_OFSWDF70-y-4af7Q2U4Z1fUDjkfeeDYIkHljecKLJiTPDbemGN-RCIh1RGgryChgEK1ng8BFJ8cqkgARNLW_yOxxdz_cLnhqXp1eP3xc8CCVvO6R7JT53t28ubvwEAAP__0FeMNQ)
- [How do you know whether an automated evaluator is trustworthy? (Week 2)](https://link.courses.maven.com/c/eJws0MHOpCAQBOCnkVsbQEQ8cNiLr2Eauv31HxVH0Mm8_WZm9_qlKqkUeUNShVawV12vGqWtk4I3XNYxrpizD2dCipjLfy3vg_0rnY88p0Pwfo___LoW8seZqJaToyn2DoLUEgxaCUgUoaHY9l1wjoIVs5fWsrMyGN2yjq5T3JBCO7XYux6DEYvXUlslpVWuVcrVTTCxm6yRtuHOkq6MjOk6M-d6w5v3OqZNLHmczrSNX_EDrpnF6udSjlw1fyo9VHqYceO1Jr4rPYQ1_VR6OFIuudID37hmmPD5TTZPmNMLKMECjz29YJlggYg7lPPKBbY34FXShoUJPlVx-g33X-byi48Zz8rIn88932k5zimt40K-b6wRt9d_AwAA__9_v3xo)
- [When is synthetic data useful, and when can it mislead you? (Week 1)](https://link.courses.maven.com/c/eJws0EGSpCAQheHTyA4DENFasJiN1zASMi3sRrFJyo6-_cTU9PaLt3jxo7eodBgFeT099KCNm5WgA_a8xgzMPtQCGIHbr7afi_x3qZ-cyiXovNf__nrt6K9asFfbjFt8zDIoo6QFpyQgRjlgHB9TmGcMTiSPIZjNAU12noKGyVg1OjAjRLVNOBixe6OM00o5PY9az_0QbJw2Z5UbaHJoOqtieVUm7g-46exjOcTO61bLsb7FL5CZRPaptYu74U9nls4sCQ7KPdLdmSXk8uzMchVu3JmFbsgsN_h6L4cv-Z2gyZ1lSyQDcZNwXbVATHIrVT7ppAptP5-Sf86WqO1RIjQQ1R9wfhC1D_hMUDurnv86vT9yTKXkdUf_GJwVtzd_AwAA__-LM4DB)
- [Where synthetic data can be unreliable (Week 1)](https://link.courses.maven.com/c/eJws0MGSpCAQBNCvkRsGFor0gcNe_A2joMqRGRQHaCf67ze2Z4_5Ig8ZSW4kNfhJsBvmx6AHMFYJPjCmNSSs1fmSkQLW9l_b62L3k8tX3fMl-LzXX38-I7mrZOrVZmkLDyu9AiVHNEoiUZCawvSYvbXkjdidUSPhPAHYScFEsyZGmnUAGwDYoIgOFJhBKTPYaRhsr_0Y5s2MymieDUE3qpCfpXLtD7z57EM-RKzrVvKxvsUtmCqL5PbWrtrpPx0sHSw7Hpx64ruDxaf80cFy5dpqBwvfmKrc8Pvd1N8SC8u2c2FZA59YYq7y5ze_zrZzi0ESNpQHvuSZm_QsC6eIPrEo7sDzk7l94teOpRvVx7-z3kNr2HNOayT30GYUt4O_AQAA__-2aYIs)
