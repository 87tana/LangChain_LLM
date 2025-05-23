# -*- coding: utf-8 -*-
"""DocumentLoading.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1a6vVwzbCpbsRtSl-5mC7t3CF7oWef4Ox
"""

from google.colab import drive
drive.mount('/content/drive/', force_remount=True)

openai_api_key = ""

import warnings
warnings.filterwarnings('ignore')

import os
import openai
import sys

!pip install langchain  --quiet

!pip install langchain-community langchain-core --quiet

! pip install pypdf --quiet

"""## PDFs¶

- Load a PDF transcript from Andrew Ng's famous CS229 course! These documents are the result of automated transcription so words and sentences are sometimes split unexpectedly.
"""

from langchain.document_loaders import PyPDFLoader

loader = PyPDFLoader("/content/drive/MyDrive/Project_Experiments/DeepLearning_LangChain/docs/cs229_lectures/MachineLearning-Lecture01.pdf")
pages = loader.load()

"""### Each page is a Document.

### A Document contains text (page_content) and metadata.

"""

len(pages)

page = pages[0]
page

print(page.page_content[0:500])

page.metadata

"""## YouTube"""

#from langchain.document_loaders.generic import GenericLoader,  FileSystemBlobLoader --> deprecated
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.blob_loaders import FileSystemBlobLoader

from langchain.document_loaders.parsers import OpenAIWhisperParser  #use openAi whisper model speech to text. youtube audio to text format
from langchain.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader  #load audio file from youtube

!pip install yt_dlp --quiet
  !pip install pydub  --quiet

#save_dir = "/content/drive/MyDrive/Project_Experiments/DeepLearning_LangChain/docs/Stanford CS229： Machine Learning Course, Lecture 1 - Andrew Ng (Autumn 2018)"

from pathlib import Path

# Replace the value below with your actual key
os.environ["OPENAI_API_KEY"] = ""

# (optional sanity check)
import openai
print("OpenAI key loaded:", bool(openai.api_key or os.getenv("OPENAI_API_KEY")))

"""- GenericLoader is the combination of youtube audio loader and openAI whisper . sppech to text"""

url = "https://www.youtube.com/watch?v=jGwO_UgTS7I"
#save_dir = "docs/youtube/"
save_dir = Path("/content/drive/MyDrive/Project_Experiments/DeepLearning_LangChain/docs/youtube/")

loader = GenericLoader(
    #YoutubeAudioLoader([url],save_dir),  # fetch from youtube
    FileSystemBlobLoader(str(save_dir), glob="*.m4a"),   #fetch locally
    OpenAIWhisperParser()
)
docs = loader.load()

docs[0].page_content[0:500]

"""## URLs"""

from langchain.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://github.com/basecamp/handbook/blob/master/titles-for-programmers.md")

docs = loader.load()

docs[0].page_content[0:500]

"""## Notion

- Follow steps here for an example Notion site such as this one:

    Duplicate the page into your own Notion space and export as Markdown / CSV.
    Unzip it and save it as a folder that contains the markdown file for the Notion page.


"""

from langchain.document_loaders import NotionDirectoryLoader
loader = NotionDirectoryLoader("/content/drive/MyDrive/Project_Experiments/DeepLearning_LangChain/docs/Notion_DB/")


docs = loader.load()

print(docs[0].page_content[0:500])

docs[0].metadata