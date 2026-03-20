from filters import matches_title, matches_location, is_excluded, is_ai_role, matches_salary


class TestMatchesTitle:
    def test_senior_software_engineer(self):
        assert matches_title("Senior Software Engineer")

    def test_staff_software_engineer(self):
        assert matches_title("Staff Software Engineer")

    def test_senior_backend_engineer(self):
        assert matches_title("Senior Backend Engineer")

    def test_principal_engineer(self):
        assert matches_title("Principal Software Engineer")

    def test_lead_platform_engineer(self):
        assert matches_title("Lead Platform Engineer")

    def test_senior_swe(self):
        assert matches_title("Senior SWE - Backend")

    def test_rejects_junior(self):
        assert not matches_title("Junior Software Engineer")

    def test_rejects_mining_engineer(self):
        assert not matches_title("Senior Mining Engineer")

    def test_rejects_mechanical_engineer(self):
        assert not matches_title("Senior Mechanical Engineer")

    def test_rejects_plain_engineer(self):
        assert not matches_title("Engineer")

    def test_rejects_product_manager(self):
        assert not matches_title("Senior Product Manager")

    def test_case_insensitive(self):
        assert matches_title("SENIOR SOFTWARE ENGINEER")

    def test_senior_with_extra_words(self):
        assert matches_title("Senior Software Engineer - Backend, Infrastructure")


class TestMatchesLocation:
    def test_rejects_bare_canada(self):
        assert not matches_location("Canada")

    def test_remote(self):
        assert matches_location("Remote")

    def test_vancouver(self):
        assert matches_location("Vancouver, BC")

    def test_worldwide(self):
        assert matches_location("Worldwide")

    def test_anywhere(self):
        assert matches_location("Anywhere")

    def test_remote_canada(self):
        assert matches_location("Remote - Canada")

    def test_rejects_usa_canada(self):
        assert not matches_location("USA, Canada")

    def test_vancouver_british_columbia(self):
        assert matches_location("Vancouver, British Columbia, Canada")

    def test_rejects_toronto(self):
        assert not matches_location("Toronto, Ontario, Canada")

    def test_rejects_usa_only(self):
        assert not matches_location("USA")

    def test_rejects_india(self):
        assert not matches_location("Bangalore, India")

    def test_rejects_europe(self):
        assert not matches_location("Europe")

    def test_case_insensitive(self):
        assert matches_location("REMOTE")

    def test_empty_string(self):
        assert not matches_location("")

    def test_none(self):
        assert not matches_location(None)

    def test_rejects_remote_us_only(self):
        assert not matches_location("Remote (US)")

    def test_rejects_remote_us_only_caps(self):
        assert not matches_location("REMOTE (US)")

    def test_rejects_remote_us_only_with_dash(self):
        assert not matches_location("Remote - US")

    def test_accepts_remote_us_canada(self):
        assert matches_location("Remote (US/Canada)")

    def test_accepts_remote_us_or_canada(self):
        assert matches_location("Remote US or Canada")


class TestMatchesTitleNone:
    def test_none_title(self):
        assert not matches_title(None)


class TestIsExcludedNone:
    def test_none_title(self):
        assert not is_excluded(None)


class TestIsExcluded:
    def test_junior(self):
        assert is_excluded("Junior Software Engineer")

    def test_intern(self):
        assert is_excluded("Software Engineering Intern")

    def test_manager(self):
        assert is_excluded("Engineering Manager")

    def test_director(self):
        assert is_excluded("Director of Engineering")

    def test_contractor(self):
        assert is_excluded("Senior Software Engineer (Contractor)")

    def test_contract(self):
        assert is_excluded("Contract Software Engineer")

    def test_senior_not_excluded(self):
        assert not is_excluded("Senior Software Engineer")

    def test_staff_not_excluded(self):
        assert not is_excluded("Staff Backend Engineer")


class TestIsAiRole:
    def test_ai_in_title(self):
        assert is_ai_role("Senior AI Engineer")

    def test_ml_in_title(self):
        assert is_ai_role("Staff ML Platform Engineer")

    def test_llm_in_title(self):
        assert is_ai_role("Senior LLM Infrastructure Engineer")

    def test_machine_learning_in_description(self):
        assert is_ai_role("Senior Software Engineer", "Building machine learning pipelines")

    def test_rag_in_title(self):
        assert is_ai_role("Senior Software Engineer - RAG Systems")

    def test_nlp_in_title(self):
        assert is_ai_role("Staff NLP Engineer")

    def test_agent_in_title(self):
        assert is_ai_role("Senior Software Engineer, AI Agent Platform")

    def test_not_ai(self):
        assert not is_ai_role("Senior Backend Engineer", "Building REST APIs")

    def test_empty_description(self):
        assert not is_ai_role("Senior Software Engineer")


class TestMatchesSalary:
    def test_above_minimum(self):
        assert matches_salary("$200,000 - $280,000 CAD")

    def test_below_minimum(self):
        assert not matches_salary("$150,000 - $180,000 CAD")

    def test_ca_dollar_k_above(self):
        assert matches_salary("CA$255.6K - CA$300.3K")

    def test_ca_dollar_k_below(self):
        assert not matches_salary("CA$125K - CA$150K")

    def test_hourly_kept(self):
        assert matches_salary("$90-95/hr")

    def test_monthly_kept(self):
        assert matches_salary("$50,000 per month")

    def test_none_kept(self):
        assert matches_salary(None)

    def test_empty_string_kept(self):
        assert matches_salary("")

    def test_dash_kept(self):
        assert matches_salary("—")

    def test_exactly_at_minimum(self):
        assert matches_salary("$200,000 - $200,000 CAD")

    def test_custom_minimum(self):
        assert matches_salary("$150,000 - $180,000 CAD", min_annual=150000)
        assert not matches_salary("$100,000 - $120,000 CAD", min_annual=150000)

    def test_max_value_determines(self):
        """If max of the range meets threshold, it passes."""
        assert matches_salary("$180,000 - $220,000 CAD")
