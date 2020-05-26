""" Testing the "self.set_attribute()" and "self.set_attributes()" methods
    to modify a Google search into becoming a Bing search.
    set_attribute() -> Modifies the attribute of the first matching element.
    set_attributes() -> Modifies the attribute of all matching elements. """

from seleniumbase import BaseCase


class HackingTest(BaseCase):
    def test_hack_search(self):
        self.open("https://google.com/ncr")
        self.assert_element('input[title="Search"]')
        self.set_attribute('[action="/search"]', "action", "//bing.com/search")
        self.set_attributes('[value="Google Search"]', "value", "Bing Search")
        self.update_text('input[title="Search"]', "SeleniumBase GitHub")
        self.click('[value="Bing Search"]')
        self.assert_element("h1.b_logo")
        self.click('[href*="github.com/seleniumbase/SeleniumBase"]')
        self.assert_element('[href="/seleniumbase/SeleniumBase"]')
        self.assert_true("seleniumbase/SeleniumBase" in self.get_current_url())
        self.click('[title="examples"]')
        self.assert_text("examples", "strong.final-path")
