"""Test _linkedin_description_from_page — JD extraction from posting HTML.

Uses a real LinkedIn posting page saved as a fixture.
"""
import scrape_jobs
from scrape_jobs import (
    _linkedin_description_from_page,
    _linkedin_posting_details,
    LINKEDIN_DESCRIPTION_MAX_CHARS,
)


def test_extracts_description_from_real_page(linkedin_job_posting_html):
    """Real posting page should yield a non-empty description."""
    desc = _linkedin_description_from_page(linkedin_job_posting_html)
    assert desc, "Expected non-empty description from real posting page"
    assert len(desc) > 50  # real JDs are long


def test_strips_html_tags(linkedin_job_posting_html):
    """Description should not contain HTML tags."""
    desc = _linkedin_description_from_page(linkedin_job_posting_html)
    assert "<" not in desc or ">" not in desc, (
        "Description contains HTML tags — stripping failed"
    )


def test_unescapes_html_entities():
    """HTML entities like &amp; should be unescaped."""
    html = '''
    <section>
      <div class="show-more-less-html__markup">
        <p>R&amp;D Engineering &amp; Product</p>
      </div>
    </section>
    '''
    desc = _linkedin_description_from_page(html)
    assert "&" in desc
    assert "&amp;" not in desc


def test_empty_page():
    assert _linkedin_description_from_page("") == ""


def test_none_page():
    assert _linkedin_description_from_page(None) == ""  # type: ignore[arg-type]


def test_page_without_description_div():
    """Page with no description div should return empty string."""
    html = "<html><body><h1>Job Title</h1></body></html>"
    assert _linkedin_description_from_page(html) == ""


def test_description_truncated_at_max():
    """Description should be truncated at LINKEDIN_DESCRIPTION_MAX_CHARS."""
    long_text = "A" * (LINKEDIN_DESCRIPTION_MAX_CHARS + 1000)
    html = f'''
    <section>
      <div class="show-more-less-html__markup">
        <p>{long_text}</p>
      </div>
    </section>
    '''
    desc = _linkedin_description_from_page(html)
    assert len(desc) <= LINKEDIN_DESCRIPTION_MAX_CHARS


def test_extracts_euro_salary_range_from_description(monkeypatch):
    html = """
    <section>
      <div class="show-more-less-html__markup">
        <p>Corporate Recruiter role. Salary: €3.800 – €5.000 monthly.</p>
      </div>
    </section>
    """
    monkeypatch.setattr(scrape_jobs, "fetch", lambda _url: html)
    salary, description = _linkedin_posting_details("123")
    assert salary == "€3.800 – €5.000 monthly"
    assert "Corporate Recruiter" in description


def test_extracts_pound_salary_range_from_description(monkeypatch):
    html = """
    <section>
      <div class="show-more-less-html__markup">
        <p>People Operations Manager. £45k to £60k annually.</p>
      </div>
    </section>
    """
    monkeypatch.setattr(scrape_jobs, "fetch", lambda _url: html)
    salary, _ = _linkedin_posting_details("456")
    assert salary == "£45k to £60k annually"
