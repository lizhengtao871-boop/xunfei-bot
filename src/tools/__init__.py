_imported = False


def auto_import_tools():
    global _imported
    if _imported:
        return
    from src.tools import knowledge, members, tasks, projects, notice, events, report  # noqa: F401
    _imported = True
