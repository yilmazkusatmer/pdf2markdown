<div align="center">

<h1>MarkPDFDown</h1>

[![Size]][hub_url]
[![Pulls]][hub_url]
[![Tag]][tag_url]
[![License]][license_url]
<p>A powerful tool that leverages multimodal large language models to transcribe PDF files into Markdown format.</p>

![markpdfdown](https://raw.githubusercontent.com/jorben/markpdfdown/refs/heads/master/tests/markpdfdown.png)

</div>


## Overview

MarkPDFDown is designed to simplify the process of converting PDF documents into clean, editable Markdown text. By utilizing advanced multimodal AI models, it can accurately extract text, preserve formatting, and handle complex document structures including tables, formulas, and diagrams.

## Features

- **PDF to Markdown Conversion**: Transform any PDF document into well-formatted Markdown
- **Multimodal Understanding**: Leverages AI to comprehend document structure and content
- **Format Preservation**: Maintains headings, lists, tables, and other formatting elements
- **Customizable Model**: Configure the model to suit your needs

## Demo
![](https://raw.githubusercontent.com/jorben/markpdfdown/refs/heads/master/tests/demo.png)

## Installation

```bash
conda create -n markpdfdown python=3.9
conda activate markpdfdown

# Clone the repository
git clone https://github.com/jorben/markpdfdown.git
cd markpdfdown

# Install dependencies
pip install -r requirements.txt

```
## Usage
```bash
# Set up your OpenAI API key
export OPENAI_API_KEY=<your-api-key>
# Optionally, set up your OpenAI API base
export OPENAI_API_BASE=<your-api-base>
# Optionally, set up your OpenAI API model
export OPENAI_DEFAULT_MODEL=<your-model>

# Run the application
python main.py < tests/input.pdf > output.md
```
## Advanced Usage
```bash
python main.py page_start page_end < tests/input.pdf > output.md
```

## Docker Usage
```bash
docker run -i -e OPENAI_API_KEY=<your-api-key> -e OPENAI_API_BASE=<your-api-base> -e OPENAI_DEFAULT_MODEL=<your-model> jorben/markpdfdown < tests/input.pdf > output.md
```

## Requirements
- Python 3.9+
- Dependencies listed in `requirements.txt`
- Access to the specified multimodal AI model

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch ( `git checkout -b feature/amazing-feature` )
3. Commit your changes ( `git commit -m 'feat: Add some amazing feature'` )
4. Push to the branch ( `git push origin feature/amazing-feature` )
5. Open a Pull Request

## License
This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Acknowledgments
- Thanks to the developers of the multimodal AI models that power this tool
- Inspired by the need for better PDF to Markdown conversion tools

[hub_url]: https://hub.docker.com/r/jorbenzhu/markpdfdown/
[tag_url]: https://github.com/jorben/markpdfdown/releases
[license_url]: https://github.com/jorben/markpdfdown/blob/main/LICENSE

[Size]: https://img.shields.io/docker/image-size/jorbenzhu/markpdfdown/latest?color=066da5&label=size
[Pulls]: https://img.shields.io/docker/pulls/jorbenzhu/markpdfdown.svg?style=flat&label=pulls&logo=docker
[Tag]: https://img.shields.io/github/release/jorben/markpdfdown.svg
[License]: https://img.shields.io/github/license/jorben/markpdfdown
