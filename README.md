# Gagana

<p align="center">
  <img alt="Project Banner" src="assets/images/Banner.png" width="99%" height="auto"/></br>
</p>

Recently, [Italiano and Cummins](https://arxiv.org/abs/2501.00655) introduced an elegant methodology for uncovering performance bugs in compilers. Their approach involves using a pre-trained large language model (LLM) to generate a seed program, followed by successive mutations designed to provoke unexpected behavior, even in mainstream compilers. This methodology is particularly appealing due to its language-agnostic nature: it can be adapted to different programming languages without the need to develop a dedicated fuzzer for each one. Moreover, it has proven highly effective, uncovering previously unknown (zero-day) performance bugs in widely used compilers such as Clang, ICC, and GCC.
In an effort to reproduce the results reported by Italiano and Cummins, we confirm that their technique outperforms general-purpose LLMs, such as open-source versions of LLaMA and DeepSeek, in identifying compiler performance bugs. However, we also observe that while the LLM-based approach is commendable, it lags behind tools like CSmith in terms of throughput (the number of bugs found over time) and latency (the time to discover the first bug). LLMs also require significantly greater computational resources.
Although this outcome may seem discouraging, it is important to note that we are comparing novel LLMs with a mature language-specific fuzzer. Nevertheless, as technology evolves, we expect the performance of LLM-based fuzzing to improve, potentially surpassing traditional methods in the future.

## Content

This repository contains an artifact of the entire generation and testing process for the article "On the Practicality of LLM-Based Compiler Fuzzing".