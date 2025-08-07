Here is the README file for Team OHSUpath.

The File CHANGELOG.md will contain information about feature update.


The 1-use-GCR-pipeline branch is intended to achieve the goal by using the "Gather → Cite → Respond" (GCR) pipeline.

It is planned to leverage two open-source models: deepseek-r1-8b-int8 (a large language model) and all-MiniLM-L6-v2 (a sentence-transformer). We plan to upgrade to Instructor-XL, which is also a sentence transformer but offers higher retrieval precision. The sentence-transformer will retrieves relevant information from the database based on the user's query and passes it to the LLM. The LLM is expected to reorganize the information into a more user-friendly format and presents it to the user.

The use of open-source models is driven by cost-efficiency. Creating and training a model from scratch can be prohibitively expensive, while open-source alternatives offer a fast and effective solution without reinventing the wheel. These two specific models were selected because they are lightweight enough to run on a laptop, which would significantly reduce the risk of exposing Protected Health Information (PHI), as the AI tool is designed to operate offline without transmitting data over a network. Additionally, users are expected to have the option to switch to a more advanced model that requires higher computational resources, should they seek more accurate results on more capable machines.