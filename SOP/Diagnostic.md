# Diagnostic Mode: Root Cause Analysis

## Objective

Identify the exact root cause of the issue without implementing any fixes, including potential cache-related problems.

## Investigation Process

1. Analyze relevant code files and execution paths
2. Trace data flow to identify where behavior deviates from expectations
3. Insert strategic logging statements with clear identifiers (e.g., [DIAG-1])
4. Examine environment variables and configuration that might impact behavior
5. Investigate potential cache issues:
   - Check server-side caching configuration
   - Verify browser cache state
   - Examine cache headers in responses
   - Compare development vs production caching behavior

## Cache Investigation Steps

1. **Server Cache Check**

   - Verify deployment status
   - Check server cache configuration
   - Examine static file serving settings
   - Review server logs for cache-related issues

2. **Browser Cache Analysis**

   - Check browser's cache storage
   - Verify cache headers in network requests
   - Compare cached vs server file versions
   - Test with different browsers to isolate issues

3. **Environment-Specific Checks**
   - Compare development vs production behavior
   - Verify auto-reload settings
   - Check static file serving configuration
   - Examine build process impact on caching

## Constraints

- Do not modify existing code functionality
- Do not implement or suggest fixes at this stage
- Focus solely on accurate diagnosis and evidence collection
- Document all cache-related findings separately

## Output Requirements

- Clear the terminal first (CLS) to avoid confusion with previous logs
- Add detailed, timestamped logs with contextual information
- Identify any potential failure points with confidence levels
- Document system state at critical moments in execution flow
- Include cache-specific diagnostic information:
  - Server cache status
  - Browser cache state
  - Cache headers present
  - Environment-specific caching behavior

### Confidence Level Reporting

- At the beginning of the diagnostic process, state the initial confidence level in understanding the problem and potential solutions (e.g., "Initial Confidence: 3/10").
- If the problem is immediately clear, this can be higher (e.g., "Initial Confidence: 10/10 if the issue is trivial and understood").
- If the problem is entirely unknown, state this (e.g., "Initial Confidence: 0/10 if I have no immediate hypotheses").
- Periodically, and especially after significant findings or changes in approach, provide an updated confidence level (e.g., "Confidence Update: 7/10, the recent logs have narrowed down the potential cause significantly.").
- The scale is 0 (no idea) to 10 (full understanding and clear path to solution).
- This helps the user gauge the AI's current understanding and the progress of the diagnostic effort.

### Log Location Guidance

When logging is implemented as part of this diagnostic process, the location of the generated logs will depend on the nature of the application and the type of logging added:

- **VS Code Integrated Terminal:** For Python scripts, Node.js applications, or any server-side processes that print to standard output/error, logs will typically appear here. If the AI instructs you to run a command that produces console output, this is where you'll find it.
- **Browser Developer Console:** For client-side issues (e.g., JavaScript errors, front-end behavior), logs will be found in your browser's Developer Console (usually accessed by pressing F12 and going to the "Console" tab).
- **Specific Log Files:** If the application is configured to write logs to a dedicated file, or if the AI explicitly directs logs to a file, the AI will specify the exact path to this file. The AI should prioritize using the terminal for output unless a log file is strictly necessary or already part of the application's standard logging mechanism.

\_The AI performing the diagnostics must clearly state where the logs are expected to appear. For example:

- "After running the script, please copy the output from the **Cursor / VSCode Integrated Terminal**."
- "Open your browser's Developer Tools (F12), go to the **Console tab**, reproduce the issue, and then copy any new log messages that appear."
- "I've added logging that will write to a file. Please check the contents of **`C:\temp\diag_log.txt`** after performing the action."
- "The diagnostic output will be printed directly to your **VS Code terminal** below."
  This ensures the user knows exactly where to look for the requested information.\_

## Note

All findings will be used to develop a targeted solution in the next phase. Cache-related issues should be documented separately to help distinguish between code and caching problems.
