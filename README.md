# Archive System Metadata Structure

This document outlines the structure of the metadata used in our archive system. Each document in the archive is enriched with AI-generated metadata that enhances search and retrieval functionalities. The metadata provides both physical and contextual attributes for various types of files, including text documents, images, videos, and audio files.

## Usage

This metadata structure is used by our archive system to enrich the files stored in the database. It allows for more precise search queries, better retrieval of relevant documents, and a more detailed overview of the stored files.

By leveraging AI to generate detailed metadata, we ensure that users can find exactly what they are looking for, even across different types of media such as text, images, videos, and audio files.

The table below shows the analysis of the dataset across different types of media (audio, document, image, video) for various topics. Each value represents the number of items available in the dataset for a specific topic and type.

| **Topic**                           | **Audio** | **Document** | **Image** | **Video** |
|-------------------------------------|:--------:|:------------:|:---------:|:--------:|
| **Animals in the wild**             |    8     |      6       |    10     |    8     |
| **Celebrities**                     |    8     |      4       |     9     |   10     |
| **Cultural celebrations and traditions** |    7     |      10      |    12     |    9     |
| **Gourmet dishes and culinary arts** |    7     |      7       |    14     |    8     |
| **Majestic landscapes**             |   10     |      6       |    14     |   12     |
| **Political events**                |    7     |      9       |    10     |    7     |
| **Scene of movies**                 |    9     |      6       |    10     |   10     |
| **Sport events**                    |   11     |      7       |    14     |   10     |
| **Study and work**                  |    7     |      8       |    12     |   11     |
| **Urban cityscapes**                |   12     |      9       |    15     |   11     |

## Metadata Attributes

The following table lists the attributes used to describe documents in the archive system, along with descriptions and examples:

<table>
  <thead>
    <tr>
      <th>Attribute</th>
      <th>Description</th>
      <th>Example</th>
      <th>Metadata Type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>id</code></td>
      <td>A unique identifier for the document.</td>
      <td>58677</td>
      <td rowspan="10">Physical metadata</td>
    </tr>
    <tr>
      <td><code>md5</code></td>
      <td>The MD5 hash of the document, used for ensuring data integrity.</td>
      <td>"460d9e165fc61630fd62a"</td>
    </tr>
    <tr>
      <td><code>extension</code></td>
      <td>The file extension of the document, indicating the document type (e.g., docx, pdf, txt for documents; jpeg, mp4 for images/videos).</td>
      <td>"pdf"</td>
    </tr>
    <tr>
      <td><code>size</code></td>
      <td>The size of the document in bytes.</td>
      <td>119436</td>
    </tr>
    <tr>
      <td><code>height</code></td>
      <td>The height of the document in pixels (applicable for images or videos; set to 0 for other types).</td>
      <td>1184 (for images/videos), 0 (for others)</td>
    </tr>
    <tr>
      <td><code>width</code></td>
      <td>The width of the document in pixels (applicable for images or videos; set to 0 for other types).</td>
      <td>800 (for images/videos), 0 (for others)</td>
    </tr>
    <tr>
      <td><code>duration</code></td>
      <td>The duration of the document in seconds (applicable for audio or video files; set to 0 for other types).</td>
      <td>120 (for audio/video), 0 (for others)</td>
    </tr>
    <tr>
      <td><code>density</code></td>
      <td>The density of the document (e.g., dots per inch for images; set to 0 for other types).</td>
      <td>300 (for images), 0 (for others)</td>
    </tr>
    <tr>
      <td><code>channels</code></td>
      <td>The number of channels (e.g., color channels in images or audio channels; set to 0 for documents).</td>
      <td>3 (for images), 0 (for documents)</td>
    </tr>
    <tr>
      <td><code>displayRotate</code></td>
      <td>The display rotation of the document (degrees of rotation, applicable for images/videos; set to 0 for other types).</td>
      <td>90 (for images/videos), 0 (for others)</td>
    </tr>
    <tr>
      <td><code>originalName</code></td>
      <td>The original name of the document.</td>
      <td>"research_paper_computing.pdf"</td>
      <td rowspan="2">Custom metadata</td>
    </tr>
    <tr>
      <td><code>category</code></td>
      <td>The category of the document, including folder ID and title where it is stored.</td>
      <td>{ "id": 42, "title": "Research Papers" }</td>
    </tr>
    <tr>
      <td><code>desc</code></td>
      <td>A brief description of the document content.</td>
      <td>"A comprehensive research paper on quantum computing."</td>
      <td rowspan="6">AI metadata</td>
    </tr>
    <tr>
      <td><code>textData</code></td>
      <td>The content of the document. It should be detailed and relevant to the topic, with a minimum of 300 words (only applicable for documents).</td>
      <td>{"This document discusses advancements in artificial intelligence and machine learning, focusing on..."}</td>
    </tr>
    <tr>
      <td><code>stt</code></td>
      <td>A transcript of spoken text (if applicable), including timestamps and speaker information.</td>
      <td>List of <code>SttData</code> objects (for audio/video)</td>
    </tr>
    <tr>
      <td><code>narrationStt</code></td>
      <td>An object containing structured data for narration transcripts (applicable for audio/video; set to {None} for other types).</td>
      <td>{ "sttData": [...], "id": 12345 } (for audio/video), None (for others)</td>
    </tr>
    <tr>
      <td><code>people</code></td>
      <td>A list of people mentioned in the document metadata, with detailed information.</td>
      <td>{ "id": 1, "name": "John Doe", "dateOfBirth": "1990-01-01" }</td>
    </tr>
    <tr>
      <td><code>organizations</code></td>
      <td>A list of organizations mentioned in the document metadata, with detailed information.</td>
      <td>{ "id": 1, "name": "OpenAI" }</td>
    </tr>
  </tbody>
</table>

## Metadata Example

Here is an example JSON object representing the metadata for a sample document:

```json
{
  "id": 58677,
  "md5": "460d9e165fc61630fd62a",
  "extension": "pdf",
  "size": 119436,
  "height": 0,
  "width": 0,
  "duration": 0,
  "density": 0,
  "channels": 0,
  "displayRotate": 0,
  "originalName": "research_paper_computing.pdf",
  "desc": "A comprehensive research paper on quantum computing.",
  "textData": {"This document discusses advancements in artificial intelligence and machine learning, focusing on..."},
  "stt": null,
  "narrationStt": null,
  "category": { "id": 42, "title": "Research Papers" },
  "people": [{ "id": 1, "name": "John Doe", "dateOfBirth": "1990-01-01" }],
  "organizations": [{ "id": 1, "name": "OpenAI" }]
}
