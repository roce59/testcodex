"""
Windows Service wrapper for the diagnostic agent.

Install as a service:
    python service.py install

Start/stop:
    python service.py start
    python service.py stop

Remove:
    python service.py remove

Requires: pip install pywin32
"""
import sys
import os

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


SERVICE_NAME = "TestcodexDiagAgent"
SERVICE_DISPLAY_NAME = "Testcodex Diagnostic Agent"
SERVICE_DESCRIPTION = "IT fleet management diagnostic agent — exposes REST API for remote diagnostics."


if HAS_WIN32:
    class DiagAgentService(win32serviceutil.ServiceFramework):
        _svc_name_ = SERVICE_NAME
        _svc_display_name_ = SERVICE_DISPLAY_NAME
        _svc_description_ = SERVICE_DESCRIPTION

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self._stop_event = win32event.CreateEvent(None, 0, 0, None)
            self._server = None

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            if self._server:
                self._server.should_exit = True
            win32event.SetEvent(self._stop_event)

        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ""),
            )
            self._run()

        def _run(self):
            import uvicorn
            # Listen on all interfaces when running as a service
            config = uvicorn.Config(
                "main:app",
                host="0.0.0.0",
                port=8000,
                log_level="info",
            )
            self._server = uvicorn.Server(config)
            self._server.run()


def main():
    if not HAS_WIN32:
        print("pywin32 is required to manage the Windows service.")
        print("Install with: pip install pywin32")
        sys.exit(1)

    if len(sys.argv) == 1:
        # Called by SCM
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DiagAgentService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DiagAgentService)


if __name__ == "__main__":
    main()
