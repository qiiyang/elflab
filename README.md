# ElfLab
### A python-based laboratory data collection and instrument control software

Currently laboratory instrument controls and data collections are typically implemented with LabView or Matlab. However these popular approaches have their drawbacks. Both software are proprietary and closed-source in nature, which masks key implementation details in black boxes. Specifically for LabView, while its graphical programming is easy to visualize, maintaining and updating large projects are difficult, especially those involve complex logical structures. The text-based MatLab, on the other hand, suffers from issues such as slow disk operations, vague programming paradigm and lack of portability and extensibility.

This python-based software, ElfLab, is intended to provide an alternative platform for laboratory data collection. Compared to LabView or MatLab, besides the usual benefit of being open source, it benefits from python's concise, object-oriented approach, and a balance between being high-level and rigorous. As results, ElfLab is highly modular, easy to read, easy to customize and easy to extend.

### Key features:
* Modular Design: highly customizable modules for data-collection, data-logging, data-plotting, instrument control GUI and data-analysis
* Parallel Processing: To avoid bottlenecks in data-collection, independent threads and processes for data-collection, data-logging and data-plotting

Start with _examples_ folder for demonstrations / examples.

![He-3 Demo](https://github.com/qiiyang/elflab/blob/master/examples/001He3Demo.png)
