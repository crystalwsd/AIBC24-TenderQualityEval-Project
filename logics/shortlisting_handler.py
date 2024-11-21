from helper_functions import valuelist as vl
from helper_functions import llm

def get_ShortlistProposalEvaluation():

    try: 
        prompt = f"""Question:
            You are an expert to evaluate a list of shortlisted tender proposals.
            Do the following to help user to evaluate proposal.

            step 1: Retrieve all proposal results documents given in the context and compare the score of similar area of assessments and any sub area of assessment \
                    among all proposals.
            step 2: For each area of assessment of Quality factor, sort and rank to show the score stated in proposal result document in descending order
            step 3: Compare among the proposals and summarize the reason and state justification for the proposal with the highest score level achieved, make comparison to the other proposals.
                    Make this summary as comprehensive and informative as possible, including stating what stands out with examples from proposal.
            step 4: Complete results of assessment for with the below structure.

            <for each Area of Assessment of the Quality Factor, evaluate all the proposals and present result in below format>
                Category : , Quality Factor:
                    Area of Assessment: <name of Area of Assessment and if any, Assessment Criteria under Area of Assessment>   
                            <list out the below score level for each proposal with highest score at the top>         
                            Proposal document name: , Level/Score: <Level, Score correspond to the criteria which is met by the proposal>
                            Summary: <Your response should be comprehensive and informative to help evalulator understand reason and justification for the ranking. \
                                    State what the proposal is lacking or excel in with relevance to the area of assessment and criteria. \
                                        give example on how proposal is determined as the Level>

            step 5: Base on the above results of assessment for all area of assessments, recommend the overall highest ranking proposal.
            step 6: state conclusion to explain why for the recommended highest ranking proposal in details.
            
            Do step by step to derive the results of shortlist proposals evaluation.
        """

        ending_instruction = """
            Response in professional manner.
            Make sure the statements are factually accurate and only base on information in the proposals.

        """
        #        Evaluation shall include all categories in the {vl.doc_category.evaljson}.
            #If you do not know, state no answer.
        finalprompt = prompt + ending_instruction
        
        #query = f"evaluate tender proposal {proposal_docname} document against the tender evaluation plan"
        #response = llm.get_RAGChainResponse(finalprompt, max_tokens=4000, collectionname=vl.COLLECTIONNAME_RESULT)
        #return response['result']

        doc_response = llm.get_SimilaritySearch(prompt)
        #context = "\n".join([doc.page_content for doc in doc_response])

        system_prompt = f"""
            Use the following pieces of context if any, as well as the context given in question to answer the question at the end.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            context: {doc_response}
        """

        #get LLM response
        finalprompt = system_prompt + prompt + ending_instruction
        response = llm.get_completion(finalprompt, max_tokens=3000)
        return response
    
    except Exception as e:
        print(f"Error in get_ShortlistProposalEvaluation for file : {e}")