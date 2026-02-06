class DDCError(RuntimeError):
    """Base class for DDC errors."""

class DDCCommandError(DDCError):
    """Raised when a DDC command fails."""
    def __init__(self,message:str, stderr: str | None = None):
        super().__init__(message)
        self.stderr = stderr or ""

class DDCParseError(DDCError):
    """Raised when parsing DDC output fails."""
    