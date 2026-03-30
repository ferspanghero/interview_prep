from unittest.mock import patch, MagicMock
import pytest
from salary_enricher import (
    extract_salary,
    normalize_salary,
    enrich_salaries,
    extract_numbers,
    is_plausible_salary,
    _fetch_salary_from_url,
)


# ---------------------------------------------------------------------------
# extract_salary — real description snippets from ground truth
# ---------------------------------------------------------------------------

class TestExtractSalary:
    """Every test case is a real description snippet from jobspy results."""

    # --- CA$/C$ prefix format ---

    def test_ca_dollar_k_suffix(self):
        text = r"Compensation Range: CA$255\.6K \- CA$300\.3K"
        assert extract_salary(text) is not None
        nums = extract_numbers(extract_salary(text))
        assert min(nums) == pytest.approx(255600, rel=0.01)
        assert max(nums) == pytest.approx(300300, rel=0.01)

    def test_ca_dollar_k_klue(self):
        text = r"Compensation Range: CA$145K \- CA$183K"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(145000, rel=0.01)
        assert max(nums) == pytest.approx(183000, rel=0.01)

    def test_ca_dollar_k_netgear(self):
        text = r"Compensation Range: CA$141K \- CA$164K"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(141000, rel=0.01)

    def test_ca_dollar_full_amount_tigera(self):
        text = r"Salary range: CA$125,000 to CA$150,000"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(125000)
        assert max(nums) == pytest.approx(150000)

    def test_ca_dollar_k_hopper(self):
        text = r"Compensation Range: CA$200K \- CA$300K"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(200000, rel=0.01)
        assert max(nums) == pytest.approx(300000, rel=0.01)

    def test_ca_dollar_k_flagler(self):
        text = r"Compensation Range: CA$150K \- CA$200K"
        sal = extract_salary(text)
        assert sal is not None

    def test_c_dollar_inworld(self):
        text = r"range for this full\-time position is C$180,000\-$C260,000\."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(180000)
        assert max(nums) == pytest.approx(260000)

    # --- CAD prefix format ---

    def test_cad_dollar_k_annually(self):
        text = r"salary range for this position is: **CAD $90K\-$120K annually.**"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(90000, rel=0.01)
        assert max(nums) == pytest.approx(120000, rel=0.01)

    def test_cad_dollar_range_lattice(self):
        text = r"cash salary for this role is CAD $146,250 \- CAD $195,000\."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(146250)
        assert max(nums) == pytest.approx(195000)

    def test_cad_dollar_range_lattice_senior(self):
        text = r"salary for this role is CAD $123,750 \- CAD $165,000\."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(123750)

    def test_cad_dollar_microsoft(self):
        text = r"range for this role across Canada is CAD $114,400 \- CAD $203,900 per year."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(114400)
        assert max(nums) == pytest.approx(203900)

    def test_cad_no_dollar_iren(self):
        text = r"base salary for this role starts at CAD$135,000 \- 155,000/annum."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(135000)
        assert max(nums) == pytest.approx(155000)

    def test_cad_semtech(self):
        text = r"pay range for this position is CAD $76,000 \- $86,000\."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(76000)
        assert max(nums) == pytest.approx(86000)

    def test_cad_between_onesignal(self):
        text = r"full\-time position is between CAD $225,000 and CAD $255,000\."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(225000)
        assert max(nums) == pytest.approx(255000)

    # --- $ range format ---

    def test_dollar_range_basic(self):
        text = r"salary range for this role is $145,000 \- $165,000 CAD."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(145000)
        assert max(nums) == pytest.approx(165000)

    def test_dollar_range_no_space_before_dash(self):
        text = r"full\-time position is $252,000\- $308,000, plus equity"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(252000)
        assert max(nums) == pytest.approx(308000)

    def test_dollar_range_with_decimals(self):
        text = r"range between $100,000\.00\-$120,000\.00 CAD in on target earnings"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(100000)
        assert max(nums) == pytest.approx(120000)

    def test_dollar_range_asana(self):
        text = r"base salary range is between $211,000 \- $240,000 CAD."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(211000)
        assert max(nums) == pytest.approx(240000)

    def test_dollar_range_asana_cad_in_middle(self):
        text = r"salary range is between $176,000 CAD \- $200,000 CAD."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(176000)
        assert max(nums) == pytest.approx(200000)

    def test_dollar_range_grafana(self):
        text = r"compensation range for this role is $186,368 \- $223,642 CAD."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(186368)
        assert max(nums) == pytest.approx(223642)

    def test_dollar_range_henry_schein_bold(self):
        text = r"range for this position is between **$155,000 CAD – $195,000 CAD**"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(155000)
        assert max(nums) == pytest.approx(195000)

    def test_dollar_range_boomi(self):
        text = r"Vancouver hub ranges from $129,388 \- $161,735 CAD annually"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(129388)

    def test_dollar_range_infoblox(self):
        text = r"salary for this position in Burnaby: $129,900 \- $185,000"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(129900)
        assert max(nums) == pytest.approx(185000)

    def test_dollar_range_fortinet(self):
        text = r"position is expected to be between $117,500 \- $143,700 annually"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(117500)

    def test_dollar_range_procurify_bold(self):
        text = r"**Base Salary Range:** **$146,000\- $182,000 CAD**"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(146000)
        assert max(nums) == pytest.approx(182000)

    def test_dollar_range_rivian(self):
        text = r"Salary range for Vancouver applicants: $137,300 \- $181,890 CAD."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(137300)
        assert max(nums) == pytest.approx(181890)

    def test_dollar_range_safe_fleet_yr(self):
        text = r"**Salary: $125,000 \- $145,000/yr CAD**"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(125000)
        assert max(nums) == pytest.approx(145000)

    def test_dollar_range_openphone(self):
        text = r"position in Canada is $192,000 \- $212,000 CAD, plus equity"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(192000)
        assert max(nums) == pytest.approx(212000)

    def test_dollar_range_omnissa(self):
        text = r"range for this role in Canada is $285,000 \- $323,050 CAD per year"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(285000)
        assert max(nums) == pytest.approx(323050)

    def test_dollar_range_omnissa_decimals(self):
        text = r"salary for this role is between $152,200\.00 \- $253,650\.00* *per year"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(152200)
        assert max(nums) == pytest.approx(253650)

    def test_dollar_range_workstream(self):
        text = r"salary range for this role is between $150,000\-$200,000 CAD in British Columbia"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(150000)
        assert max(nums) == pytest.approx(200000)

    def test_dollar_range_suger_cad_year(self):
        text = r"Base Salary Range: $150,000 \- $200,000 CAD/year"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(150000)

    def test_dollar_range_prenuvo(self):
        text = r"base salary for this role ranges from $155,000 \- $175,000 in local currency"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(155000)
        assert max(nums) == pytest.approx(175000)

    def test_dollar_range_paramount(self):
        text = r"range for this full\-time position is $145,000 \- $190,000 CAD."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(145000)
        assert max(nums) == pytest.approx(190000)

    # --- $X and $Y format ---

    def test_dollar_and_autodesk(self):
        text = r"For Canada\-BC based roles, we expect a starting base salary between $107,000 and $157,300\."
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(107000)
        assert max(nums) == pytest.approx(157300)

    def test_dollar_and_simple(self):
        text = "salary between $120,000 and $180,000"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(120000)
        assert max(nums) == pytest.approx(180000)

    # --- $X to $Y format ---

    def test_dollar_to_rival(self):
        text = r"salary range for this position is $120,000 to $150,000, with the upper portion"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(120000)
        assert max(nums) == pytest.approx(150000)

    # --- $Xk-$Yk format ---

    def test_dollar_k_urbanlogiq(self):
        text = r"staff\-level engineer at $140k\-$180k plus equity"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(140000, rel=0.01)
        assert max(nums) == pytest.approx(180000, rel=0.01)

    def test_dollar_k_train_with_ellie(self):
        text = r"base salary range for this role is $190K\-220K depending on level"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(190000, rel=0.01)
        assert max(nums) == pytest.approx(220000, rel=0.01)

    # --- Hourly rate format ---

    def test_hourly_randstad(self):
        text = r"Hour Rate Range: $75\-85/hr INC"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(75)
        assert max(nums) == pytest.approx(85)

    def test_hourly_swim(self):
        text = r"this role pays between $90\-95 per hour"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(90)
        assert max(nums) == pytest.approx(95)

    # --- Monthly rate format ---

    def test_monthly_timecash(self):
        text = r"Pay: $50,000\.00\-$100,000\.00 per month"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(50000)
        assert max(nums) == pytest.approx(100000)

    # --- Em dash / special dash ---

    def test_em_dash_databricks(self):
        text = "Canada Pay Range $173,400—$238,350 CAD"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(173400)
        assert max(nums) == pytest.approx(238350)

    def test_en_dash_cronometer(self):
        text = "Base annual salary range: $115,000 – $125,000"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(115000)
        assert max(nums) == pytest.approx(125000)

    # --- Bare number + CAD format ---

    def test_bare_numbers_cad_family_innovation(self):
        text = r"Pay: $125,000\.00\-$165,000\.00 per year"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(125000)
        assert max(nums) == pytest.approx(165000)

    def test_vopay_per_year(self):
        text = r"**Compensation** $100,000\.00 \- $130,000\.00 per year"
        sal = extract_salary(text)
        assert sal is not None
        nums = extract_numbers(sal)
        assert min(nums) == pytest.approx(100000)
        assert max(nums) == pytest.approx(130000)

    # --- Noise rejection ---

    def test_rejects_fundraising(self):
        text = "Giga has recently raised a $61M Series A and has several paying customers"
        assert extract_salary(text) is None

    def test_rejects_wellness_stipend(self):
        text = "Catered lunch daily * Dinner stipend * $150/month wellness benefit"
        assert extract_salary(text) is None

    def test_rejects_insurance_amount(self):
        text = "Basic life insurance in the amount of $50,000 or 1 X's your salary"
        assert extract_salary(text) is None

    def test_rejects_401k_match(self):
        text = "3% of your pay that you contribute and $0.50 on the dollar on the next 2%"
        assert extract_salary(text) is None

    def test_rejects_mental_health_benefit(self):
        text = "$1,000 annual mental health benefits with Canada Life"
        assert extract_salary(text) is None

    def test_rejects_revenue_figure(self):
        text = "processes over 110M transactions and $257B annually"
        assert extract_salary(text) is None

    def test_rejects_fundraising_large(self):
        text = "Hopper has raised over $750 million USD of private capital"
        assert extract_salary(text) is None

    def test_rejects_industry_size(self):
        text = "transforming the industrial supply chain ($10T industry) with AI"
        assert extract_salary(text) is None

    def test_rejects_home_office(self):
        text = "A $500 Home office setup if you're a remote employee"
        assert extract_salary(text) is None

    def test_rejects_empty_string(self):
        assert extract_salary("") is None

    def test_rejects_no_salary(self):
        text = "We offer competitive compensation, equity, and comprehensive benefits."
        assert extract_salary(text) is None


# ---------------------------------------------------------------------------
# normalize_salary
# ---------------------------------------------------------------------------

class TestNormalizeSalary:
    def test_strips_prefix_salary(self):
        assert normalize_salary("salary: $120,000 - $150,000") == "$120,000 - $150,000"

    def test_strips_prefix_base(self):
        assert normalize_salary("base $120,000 - $150,000") == "$120,000 - $150,000"

    def test_strips_prefix_compensation(self):
        assert normalize_salary("compensation: $120,000 - $150,000") == "$120,000 - $150,000"

    def test_collapses_whitespace(self):
        assert normalize_salary("$120,000  -  $150,000") == "$120,000 - $150,000"

    def test_none_input(self):
        assert normalize_salary(None) is None

    def test_truncates_long(self):
        long_sal = "$100,000 - $200,000 CAD plus equity plus benefits plus bonus plus more"
        result = normalize_salary(long_sal)
        assert len(result) <= 60
        assert result.endswith("...")


# ---------------------------------------------------------------------------
# extract_numbers
# ---------------------------------------------------------------------------

class TestExtractNumbers:
    def test_plain_numbers(self):
        assert extract_numbers("$120,000 - $180,000") == [120000.0, 180000.0]

    def test_k_suffix(self):
        assert extract_numbers("CA$145K - CA$183K") == [145000.0, 183000.0]

    def test_decimals(self):
        nums = extract_numbers("$100,000.00-$120,000.00")
        assert nums[0] == pytest.approx(100000)
        assert nums[1] == pytest.approx(120000)

    def test_mixed(self):
        nums = extract_numbers("CA$255.6K - CA$300.3K")
        assert nums[0] == pytest.approx(255600, rel=0.01)
        assert nums[1] == pytest.approx(300300, rel=0.01)

    def test_empty(self):
        assert extract_numbers("no numbers here") == []


# ---------------------------------------------------------------------------
# is_plausible_salary
# ---------------------------------------------------------------------------

class TestIsPlausibleSalary:
    def test_annual_plausible(self):
        assert is_plausible_salary("$120,000 - $150,000", [120000, 150000]) is True

    def test_annual_too_low(self):
        assert is_plausible_salary("$500 setup", [500]) is False

    def test_hourly_plausible(self):
        assert is_plausible_salary("$75-85/hr", [75, 85]) is True

    def test_hourly_too_low(self):
        assert is_plausible_salary("$5/hr", [5]) is False

    def test_monthly_plausible(self):
        assert is_plausible_salary("$50,000 per month", [50000]) is True

    def test_monthly_too_low(self):
        assert is_plausible_salary("$150/month", [150]) is False

    def test_empty_nums(self):
        assert is_plausible_salary("text", []) is False


# ---------------------------------------------------------------------------
# enrich_salaries — the new public API
# ---------------------------------------------------------------------------

class TestEnrichSalaries:
    def test_enriches_job_with_salary_in_description(self):
        jobs = [{"title": "SWE", "salary": None, "description": "Base salary: $150,000 - $200,000 CAD"}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is not None
        assert "150,000" in result[0]["salary"]

    def test_skips_job_that_already_has_salary(self):
        jobs = [{"title": "SWE", "salary": "$100K-$150K", "description": "Base salary: $200,000 - $300,000 CAD"}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] == "$100K-$150K"

    def test_skips_job_with_no_description(self):
        jobs = [{"title": "SWE", "salary": None, "description": ""}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is None

    def test_skips_job_with_no_salary_in_description(self):
        jobs = [{"title": "SWE", "salary": None, "description": "AI platform engineer working on ML pipelines"}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is None

    def test_handles_missing_description_key(self):
        jobs = [{"title": "SWE", "salary": None}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is None

    def test_enriches_multiple_jobs(self):
        jobs = [
            {"title": "SWE", "salary": None, "description": "Range: $120,000 - $150,000 CAD"},
            {"title": "Staff", "salary": None, "description": "No salary info here"},
            {"title": "Lead", "salary": "$200K", "description": "Range: $280,000 - $320,000 CAD"},
        ]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is not None
        assert result[1]["salary"] is None
        assert result[2]["salary"] == "$200K"

    def test_empty_list(self):
        assert enrich_salaries([]) == []

    def test_returns_same_list(self):
        jobs = [{"title": "SWE", "salary": None, "description": ""}]
        result = enrich_salaries(jobs)
        assert result is jobs

    def test_normalizes_extracted_salary(self):
        jobs = [{"title": "SWE", "salary": None, "description": r"salary: $150,000 \- $200,000 CAD"}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is not None
        assert not result[0]["salary"].startswith("salary")

    @patch("salary_enricher.requests.get")
    def test_fetches_url_when_no_description(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html>Base salary: $200,000 - $280,000 CAD</html>"
        mock_get.return_value = mock_resp
        jobs = [{"title": "SWE", "salary": None, "description": "", "url": "https://example.com/job/1"}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is not None
        assert "200,000" in result[0]["salary"]
        mock_get.assert_called_once()

    @patch("salary_enricher.requests.get")
    def test_skips_fetch_when_description_exists(self, mock_get):
        jobs = [{"title": "SWE", "salary": None, "description": "No salary info here", "url": "https://example.com/job/1"}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is None
        mock_get.assert_not_called()

    @patch("salary_enricher.requests.get")
    def test_handles_fetch_failure(self, mock_get):
        mock_get.side_effect = Exception("timeout")
        jobs = [{"title": "SWE", "salary": None, "description": "", "url": "https://example.com/job/1"}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is None

    @patch("salary_enricher.requests.get")
    def test_linkedin_extracts_from_description_div(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = """
        <span class="main-job-card__salary-info">CA$150,000.00 - CA$200,000.00</span>
        <div class="show-more-less-html__markup">Salary range: $120,000 - $160,000 CAD</div>
        """
        mock_get.return_value = mock_resp
        jobs = [{"title": "SWE", "salary": None, "description": "", "url": "https://www.linkedin.com/jobs/view/12345"}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is not None
        assert "120,000" in result[0]["salary"]
        assert "150,000.00" not in result[0]["salary"]

    @patch("salary_enricher.requests.get")
    def test_fetches_url_when_description_key_missing(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html>Comp: $180,000 - $220,000 CAD</html>"
        mock_get.return_value = mock_resp
        jobs = [{"title": "SWE", "salary": None, "url": "https://example.com/job/1"}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is not None
        mock_get.assert_called_once()

    @patch("salary_enricher.requests.get")
    def test_no_fetch_when_no_url(self, mock_get):
        jobs = [{"title": "SWE", "salary": None, "description": ""}]
        result = enrich_salaries(jobs)
        assert result[0]["salary"] is None
        mock_get.assert_not_called()


# ---------------------------------------------------------------------------
# _fetch_salary_from_url
# ---------------------------------------------------------------------------

class TestFetchSalaryFromUrl:
    @patch("salary_enricher.requests.get")
    def test_extracts_salary_from_html(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<div>Salary: $150,000 - $200,000 CAD</div>"
        mock_get.return_value = mock_resp
        assert _fetch_salary_from_url("https://example.com/job") is not None

    @patch("salary_enricher.requests.get")
    def test_returns_none_on_no_salary(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<div>Great company, great benefits</div>"
        mock_get.return_value = mock_resp
        assert _fetch_salary_from_url("https://example.com/job") is None

    @patch("salary_enricher.requests.get")
    def test_returns_none_on_error(self, mock_get):
        mock_get.side_effect = Exception("connection refused")
        assert _fetch_salary_from_url("https://example.com/job") is None

    @patch("salary_enricher.requests.get")
    def test_returns_none_on_403(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.raise_for_status.side_effect = Exception("403")
        mock_get.return_value = mock_resp
        assert _fetch_salary_from_url("https://example.com/job") is None

    @patch("salary_enricher.requests.get")
    def test_linkedin_uses_description_div_only(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = """
        <span class="main-job-card__salary-info">CA$300,000.00 - CA$400,000.00</span>
        <div class="show-more-less-html__markup--clamp-after-5">Range: $125,000 - $175,000 CAD</div>
        """
        mock_get.return_value = mock_resp
        result = _fetch_salary_from_url("https://www.linkedin.com/jobs/view/999")
        assert result is not None
        assert "125,000" in result
