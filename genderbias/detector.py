
from abc import abstractmethod


class BiasBoundsException(Exception):
    pass


class Issue:
    """
    An Issue is a call-out to a specific failure of a text.

    Think of an Issue as a red squiggly, and optionally, a list of
    autocorrect suggestions. For example,

        Issue(
            "Personal Life",
            "Words that reference a person's personal life",
            fix="Reference professional merits instead.
        )

    """

    positive_result = +1.0
    negative_result = -1.0

    def __init__(self, name: str, description: str = "", fix: str = "", bias=negative_result):
        """
        Create a new Issue.

        The bias indicates how strongly the flagged item might be avoided, from
        negative_result (0.0) for things to reconsider, to positive_result
        (1.0) for items which are considered favorable.

        Arguments:
            name (str): The category of the Issue (e.g. 'Personal_Life')
            description (str: ""): A plaintext description of what's wrong with
                this particular passage
            fix (str: ""): An optional recommendation for how to fix the text
            bias (float): The bias, from positive_result to negative_result

        Returns:
            None

        """
        if bias < Issue.negative_result or bias > Issue.positive_result:
            raise BiasBoundsException()

        self.name = name
        self.description = description
        self.fix = fix
        self.bias = bias

    def __str__(self):
        """
        Print a stringified version of this Issue.

        Arguments:
            None

        Returns:
            str: The Issue, formatted as: `Name: Description. (Fix)`

        """
        if self.bias != Issue.negative_result:  # Maybe users should always check for bias instead?
            return ""
        result = self.name
        if self.description:
            result += ": " + self.description
            if self.fix:
                result += " ({})".format(self.fix)
        return result


class Flag:
    """
    A flag is a callout to a particular index in the text. It includes an
    issue (what is wrong with the passage) and start-stop character indices.
    """

    def __init__(self, start: int, stop: int, issue: 'Issue') -> None:
        """
        Create a new Flag.

        Arguments:
            start (int): The start-index of the passage at fault, inclusive
            stop (int): The stop-index of the passage at fault, exclusive
            issue (Issue): The issue to tag on this passage

        Returns:
            None

        """
        self.start = start
        self.stop = stop
        if not isinstance(issue, Issue):
            raise ValueError(
                "Issue must be of type 'genderbias.Issue' but got {}".format(
                    type(issue)
                )
            )
        self.issue = issue

    def __str__(self) -> str:
        """
        Stringify the Flag.

        Arguments:
            None

        Returns:
            str: Of the form `[start-stop]: str(Issue)`

        """
        return "[{start}-{stop}]: {msg}".format(
            start=self.start,
            stop=self.stop,
            msg=str(self.issue)
        )


class Report:
    """
    A structured report with a name, optional summary (both strings) and Flags
    as defined above. Output is provided as a string.
    """

    def __init__(self, name: str) -> None:
        """
        Create a new Report with a given name (title).

        Reports act as storage for the structured data generated by a Detector.

        Arguments:
            name (str): The name/title of the Report

        Returns:
            None
        """
        self._name = name
        self._flags = []
        self._summary = None

    def __str__(self) -> str:
        """
        Generates a string from the report

        Arguments:
            None

        Returns:
            str: Multiline text
        """
        text = [self._name]
        if self._flags:
            text += [" " + str(flag) for flag in self._flags if flag.issue.bias == Issue.negative_result]
        text.append(" SUMMARY: " + (self._summary if self._summary else "[None available]"))
        return "\n".join(text)

    def add_flag(self, flag: 'Flag') -> None:
        """
        Adds a `Flag` object to the Report, marking a specific part of the text.

        Arguments:
            flag (Flag): A Flag object describing the issue

        Returns:
            None
        """
        self._flags.append(flag)

    def set_summary(self, summary: str) -> None:
        """
        Sets the summary for the report.

        Arguments:
            summary (str): The text to set as the summary.

        Returns:
            None
        """
        self._summary = summary

    def to_dict(self) -> dict:
        """
        Converts the Report into a `dict` of items, suitable for conversion to
        JSON.

        Arguments:
            None

        Returns:
            dict: str values for the keys 'name', 'summary', with 'flags' being
            a list of tuples (bias, start, stop, name, description, fix)
        """
        return dict(name=self._name,
                    summary=(self._summary if self._summary else ""),
                    flags=[(flag.start, flag.stop, flag.issue.name,
                            flag.issue.description, flag.issue.fix, flag.issue.bias)
                           for flag in self._flags]
        )


class Detector:
    """
    Abstract class for a detector. Implement this to use.
    For an example implementation tutorial, look at `docs/hacking.md`.
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_report(self, doc: 'Document'):
        """
        Returns a Report for a document.
        """
        raise NotImplementedError()

