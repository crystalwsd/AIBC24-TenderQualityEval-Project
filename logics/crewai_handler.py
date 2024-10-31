# Import the key CrewAI classes
from crewai import Agent, Task, Crew
from crewai_tools import DOCXSearchTool
from crewai_tools import JSONSearchTool
from crewai_tools import DirectorySearchTool
from crewai_tools import FileReadTool
import os
from helper_functions import valuelist as vl
import json
import streamlit as st

def CrewAIEvaluation(proposal_docname):

    tool_worddocsearch = DOCXSearchTool()
    tool_textdocsearch = FileReadTool(vl.METADATAFILEPATH)
    tool_jsondocsearch = JSONSearchTool(vl.EVALJSONFILENAME)
    #tool_dirsearch = DirectorySearchTool(os.path.join("data"))

    #dir_result = tool_dirsearch.run()

    agent_docretriever = Agent(
        role="Tender evaluation documents retriever",
        goal="Identify and extract the right document relevant to tender proposal evaluation",
        backstory="You're a document retriever for tender evaluation to identify required documents and draw content from documents\
                    make the best use of the tools provided to extract as much necessary information as possible",
        tools=[tool_textdocsearch, tool_worddocsearch, tool_jsondocsearch],
        allow_delegation=True,
        verbose=True
    )

    task_docretriever = Task(
        description="""
        1. Refer to the {docmetafile} on the list of documents, all files in the list are stored at location under directory {datadir}
        2. identify the tender evaluation plan document and retrieve
        3. identify the tender proposal document {tender proposal} and retrieve.
        4. only draw document relevant to the {query}
        """,

        expected_output="""
        list of document objects or document content relevant to evaluation stated in {query}
        """,
        agent = agent_docretriever
    )

    agent_evalplanner = Agent(
        role="Tender Evaluation Planner",
        goal="List all categories, area of evaluation assessment and their assessment criteria \
            from tender evaluation plan",
        backstory="""
            You're working on planning for a list of evaluation criteria that can determine the quality score level\
            of the tender proposal.
            You base your extraction from Tender evaluation documents retriever.
            Only reference content and all sections in tender evaluation plan document after the text 'Detailed Evaluation Approach'
            make the best use of the tools provided to extract as much necessary information as possible
        """,
        tools=[tool_textdocsearch, tool_worddocsearch, tool_jsondocsearch],
        allow_delegation=True,
        verbose=True
    )

    task_evalplanner = Task(
        description="""
        1. refer to only content in tender evaluation plan from "Detailed Evaluation Approach" and below
        2. understand how the tables are structured:
            - there are one or more category of service from tenderer, where each category has one or more table
            - each table of category is structured with the 
                Key Quality Factor (example Hiring Practices) with weightage,
                    Main area of assessment with weightage,
                         sub area of assessment (without any weightage),
                            list of criteria of different quality level correspond to score
        3. read and retrieve the information required as above and construct into structured document
        """,
        expected_output="""
        list of evaluation criteria with score level with below structure:
            Category: (example 8B)
                 Key Quality Factor (example Hiring Practices) with weightage,
                    Main area of assessment with weightage,
                         sub area of assessment (without any weightage),
                            list of criteria of different quality level with corresponding score
       
        """,
        agent = agent_evalplanner

    )

    # Creating the Crew
    crew = Crew(
        agents=[agent_docretriever, agent_evalplanner],
        tasks=[task_docretriever, task_evalplanner],
        verbose=True
    )

    query = "extract relevant documents and list down all relevant assessment criteria information including any security criteria in tender evaluation plan"
    # Running the Crew
    result = crew.kickoff(inputs={"docmetafile": vl.METADATAFILEPATH, "vectorstore": vl.VECTORDB, "datadir":os.path.join("data"), "tender proposal":proposal_docname, "query":query})
    st.session_state[vl.EVALRESULT_SESSIONNAME] = result