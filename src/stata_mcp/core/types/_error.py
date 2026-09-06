class StataMCPError(Exception):
    """Custom exception for Stata MCP related errors."""
    pass


class OSNotSupported(StataMCPError):
    """Raised when an operation is unavailable on the current OS."""

    def __init__(self):
        super().__init__("OS not supported")


class RAMLimitExceededError(StataMCPError):
    """Exception raised when Stata process exceeds configured RAM limit."""

    def __init__(self, ram_used_mb: float, ram_limit_mb: int):
        """
        Initialize RAM limit exceeded error.

        Args:
            ram_used_mb: Actual RAM usage in MB
            ram_limit_mb: Configured RAM limit in MB
        """
        self.ram_used_mb = ram_used_mb
        self.ram_limit_mb = ram_limit_mb
        message = f"Over RAM usage than config ({ram_used_mb:.0f}MB > {ram_limit_mb}MB)"
        super().__init__(message)


class StataCLINotFoundError(StataMCPError):
    """Exception raised when Stata CLI cannot be found."""

    def __init__(self):
        """Initialize Stata CLI not found error."""
        message = (
            "Stata CLI not found. Please:\n"
            "1. Install Stata 17+ with a valid license, or\n"
            "2. Configure the path in ~/.statamcp/config.toml:\n"
            "   [STATA]\n"
            "   STATA_CLI = '/path/to/stata-mp'"
        )
        super().__init__(message)
