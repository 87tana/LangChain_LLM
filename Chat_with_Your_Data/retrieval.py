# -*- coding: utf-8 -*-
"""Retrieval.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gjAj11WnnTpQRHtjD2jlHlmarHeN6qVF
"""

from google.colab import drive
drive.mount('/content/drive/', force_remount=True)

import os
import openai

openai_api_key =

#!pip install pypdf --quiet

#! pip install tiktoken --quiet
#! pip install chromadb  --quiet

!pip install lark

!pip install langchain-community langchain-core --quiet
!pip install chromadb  --quiet
!pip install tiktoken  --quiet

"""## Similarity Search"""

from langchain.vectorstores import Chroma #vectorDB
from langchain.embeddings.openai import OpenAIEmbeddings
persist_directory =  ("/content/drive/MyDrive/Project_Experiments/DeepLearning_LangChain/docs/chroma/")

embedding = OpenAIEmbeddings(openai_api_key = openai_api_key)
vectordb = Chroma(
    persist_directory = persist_directory,
    embedding_function = embedding
)

print(vectordb._collection.count())

texts = [
    """The Amanita phalloides has a large and imposing epigeous (aboveground) fruiting body (basidiocarp).""",
    """A mushroom with a large fruiting body is the Amanita phalloides. Some varieties are all-white.""",
    """A. phalloides, a.k.a Death Cap, is one of the most poisonous of all known mushrooms.""",
]

smalldb = Chroma.from_texts(texts, embedding = embedding) # chroma --> vector DB, store text and embedding so you can search or retrieve simialr text

question = "Tell me about all-white mushrooms with large fruiting bodies"

smalldb.similarity_search(question, k=2) # by similarity search -> two relevant doc without mentioneing poisionius

smalldb.max_marginal_relevance_search(question, k=2, fetch_k=3) #most relevant and most diverse

"""## Addressing Diversity: Maximum marginal relevance

- Last class we introduced one problem: how to enforce diversity in the search results.

- Maximum marginal relevance strives to achieve both relevance to the query and diversity among the results.

"""

question = "what did they say about matlab?"
docs_ss = vectordb.similarity_search(question,k=3)

docs_ss[0].page_content[:100]

docs_ss[1].page_content[:100]

docs_mmr = vectordb.max_marginal_relevance_search(question, k=3)

"""- Note the difference in results with MMR"""

docs_mmr[0].page_content[:100]

docs_mmr[1].page_content[:100]

"""## Self-query

## Addressing Specificity: working with metadata

- In last lecture, we showed that a question about the third lecture can include results from other lectures as well.

- To address this, many vectorstores support operations on metadata.

- metadata provides context for each embedded chunk.
"""

question = "what did they say about regression in the third lecture?"

docs = vectordb.similarity_search(
    question,
    k = 3,
    filter = {"source":"/content/drive/MyDrive/Project_Experiments/DeepLearning_LangChain/docs/cs229_lectures/MachineLearning-Lecture03.pdf"}
) # if we fix it manually

docs

for d in docs:
    print(d.metadata)

"""- we can use language model to do for us, insteady of hardcoded

## Addressing Specificity: working with metadata using self-query retriever

- But we have an interesting challenge: we often want to infer the metadata from the query itself.

- To address this, we can use SelfQueryRetriever, which uses an LLM to extract:

    The query string to use for vector search
    A metadata filter to pass in as well

- Most vector databases support metadata filters, so this doesn't require any new databases or indexes.
"""

from langchain.llms import OpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo # specify different fields in the metadata and what correspond to

metadata_field_info = [
    AttributeInfo(
        name="source",
        description=(
           "The lecture the chunk is from. "
           "Should be one of: "
           "/content/drive/MyDrive/Project_Experiments/DeepLearning_LangChain/docs/cs229_lectures/MachineLearning-Lecture01.pdf,"
           "/content/drive/MyDrive/Project_Experiments/DeepLearning_LangChain/docs/cs229_lectures/MachineLearning-Lecture02.pdf,"
           "/content/drive/MyDrive/Project_Experiments/DeepLearning_LangChain/docs/cs229_lectures/MachineLearning-Lecture03.pdf"
        ),
        type="string",
    ),
    AttributeInfo(
        name="page",
        description="The page from the lecture.",
        type="integer",
    ),
]

document_content_description = "Lecture notes"

llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0, openai_api_key= openai_api_key)
retriever = SelfQueryRetriever.from_llm(
    llm,
    vectordb,
    document_content_description,
    metadata_field_info,
    verbose=True
)

question = "what did they say about regression in the third lecture?"

docs = retriever.invoke(question)

docs

for d in docs:
    print(d.metadata)

"""- now only extract a relevant bit from the documents and pass those into LLM

## Additional tricks: compression

- Another approach for improving the quality of retrieved docs is compression.

- Information most relevant to a query may be buried in a document with a lot of irrelevant text.

- Passing that full document through your application can lead to more expensive LLM calls and poorer responses.

- Contextual compression is meant to fix this.
"""

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

def pretty_print_docs(docs):
    print(f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]))

# Wrap our vectorstore  # create compressor with LLM chain extractor
llm = OpenAI(temperature=0, model="gpt-3.5-turbo-instruct", openai_api_key= openai_api_key)
compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(
    base_compressor = compressor,
    base_retriever = vectordb.as_retriever()
)

question = "what did they say about matlab?"
compressed_docs = compression_retriever.get_relevant_documents(question)
pretty_print_docs(compressed_docs)

"""## Combining various techniques"""

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectordb.as_retriever(search_type = "mmr")
)

question = "what did they say about matlab?"
compressed_docs = compression_retriever.get_relevant_documents(question)
pretty_print_docs(compressed_docs)

"""## Other types of retrieval

- It's worth noting that vectordb as not the only kind of tool to retrieve documents.

- The LangChain retriever abstraction includes other ways to retrieve documents, such as TF-IDF or SVM.

"""

from langchain.retrievers import SVMRetriever
from langchain.retrievers import TFIDFRetriever

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

!pip install pypdf

# Load PDF
loader = PyPDFLoader("/content/drive/MyDrive/Project_Experiments/DeepLearning_LangChain/docs/cs229_lectures/MachineLearning-Lecture01.pdf")
pages = loader.load()
all_page_text = [p.page_content for p in pages]
joined_page_text=" ".join(all_page_text)

# Split
text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1500,chunk_overlap = 150)
splits = text_splitter.split_text(joined_page_text)

# Retrieve
svm_retriever = SVMRetriever.from_texts(splits,embedding)
tfidf_retriever = TFIDFRetriever.from_texts(splits)

question = "What are major topics for this class?"
docs_svm=svm_retriever.get_relevant_documents(question)
docs_svm[0]

question = "what did they say about matlab?"
docs_tfidf=tfidf_retriever.get_relevant_documents(question)
docs_tfidf[0]