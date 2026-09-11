from pydantic import BaseModel, Field

class CreditFeaturesSchema(BaseModel):
    is_valid_financial_document: bool = Field(
        default=True,
        description=(
            "Set to True if the input text contains coherent financial, loan, or credit details. "
            "Set to False if the input is gibberish, conversational noise, or completely unrelated to credit."
        )
    )
    loan_amnt: float = Field(description="The requested loan amount")
    term: str = Field(description="Loan term, strictly format as ' 36 months' or ' 60 months'")
    int_rate: float = Field(description="Interest rate on the loan")
    installment: float = Field(description="Monthly payment owed by the borrower")
    grade: str = Field(description="Assigned loan grade (e.g., A, B, C)")
    sub_grade: str = Field(description="Assigned loan sub-grade (e.g., B4)")
    emp_length: str = Field(description="Employment length in years, e.g. '10+ years'")
    home_ownership: str = Field(description="Home ownership status (RENT, OWN, MORTGAGE)")
    annual_inc: float = Field(description="Self-reported annual income")
    verification_status: str = Field(description="Income verification status")
    purpose: str = Field(description="Category provided by the borrower for the loan request")
    addr_state: str = Field(description="State address, e.g., 'CA'")
    dti: float = Field(description="Debt-to-income ratio")
    open_acc: float = Field(description="Number of open credit lines")
    pub_rec: float = Field(description="Number of derogatory public records")
    revol_bal: float = Field(description="Total credit revolving balance")
    revol_util: float = Field(description="Revolving line utilization rate")
    total_acc: float = Field(description="Total number of credit lines")
    mort_acc: float = Field(description="Number of mortgage accounts")
    pub_rec_bankruptcies: float = Field(description="Number of public record bankruptcies")