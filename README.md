# MCP Web Server

A powerful web crawler and browser automation server built on FastMCP that provides comprehensive web analysis capabilities through a simple API.

## Features

- **Browser Automation**: Programmatically control Chrome browser sessions
- **Web Crawling**: Extract content from websites with intelligent parsing
- **Screenshot Capture**: Take screenshots of web pages
- **JavaScript Execution**: Run JavaScript in browser sessions
- **Advanced Web Analysis**: Analyze UI/UX, layout, and component hierarchy
- **Responsive Design Testing**: Test website behavior across different screen sizes
- **Deep Web Search**: Perform multi-page, in-depth web searches

## Installation

### Prerequisites

- Python 3.10+
- Chrome/Chromium browser
- ChromeDriver (compatible with your Chrome version)

### Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd mcp_web_server
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure ChromeDriver is in the project directory or available in your PATH.
downlink = https://googlechromelabs.github.io/chrome-for-testing/

## Usage

### Starting the Server

```bash
mcp run your_path/mcp_web_server.py
```

This will start the MCP server which provides the web server functionality through various tools and resources.

### Available Tools

#### Browser Control

- `start_browser`: Initialize a new browser session
- `navigate_to_url`: Go to a specific URL
- `take_screenshot`: Capture a screenshot of the current page
- `close_browser`: Terminate a browser session
- `execute_javascript`: Run JavaScript in the browser context

#### Web Crawling

- `crawl_url`: Fetch and parse content from a URL
- `parse_html`: Parse HTML content using BeautifulSoup
- `find_selectors`: Discover useful CSS selectors in HTML content
- `get_page_html`: Get the HTML source of the current page

#### UI/UX Analysis

- `analyze_website_ui_ux`: Comprehensive analysis of a website's UI and UX
- `analyze_page_layout`: Analyze page structure and layout patterns
- `analyze_component_hierarchy`: Examine UI component relationships
- `analyze_responsive_behavior`: Test website behavior at different screen sizes

#### Advanced Web Interaction

- `click_element_and_wait`: Click an element and wait for page load
- `find_clickable_elements`: Find all interactive elements on a page
- `navigate_and_analyze`: Navigate to a new page and analyze its structure

#### Web Search

- `deep_web_search`: Perform deep searches on the web with multi-page exploration
- `answer_question_from_web`: Search the web to answer specific questions

## Architecture

The MCP Web Server is built using FastMCP, which provides a flexible framework for creating AI-powered microservices. The server exposes various tools as API endpoints that can be called programmatically.

### Key Components

- **Browser Session Management**: Handles browser initialization and control using Selenium
- **Web Crawling Engine**: Uses requests and BeautifulSoup for efficient content extraction
- **Analysis Pipeline**: Processes web pages to extract meaningful information about structure and design
- **Search Capabilities**: Implements deep web search functionality with multi-page exploration

## Configuration

The server can be configured by modifying parameters in the tool definitions within `mcp_web_server.py`. Common configuration options include:

- Default headers for web requests
- Browser options (headless mode, user agent, etc.)
- Default analysis parameters

## Dependencies

- `mcp[cli]`: MCP framework and CLI tools
- `selenium`: Browser automation
- `beautifulsoup4`: HTML parsing
- `requests`: HTTP client
- `webdriver-manager`: ChromeDriver management

## Troubleshooting

### Common Issues

1. **ChromeDriver Compatibility**: Make sure your ChromeDriver version matches your Chrome browser version
2. **Permission Errors**: Ensure ChromeDriver has proper execution permissions (`chmod +x chromedriver`)
3. **Memory Issues**: For large-scale crawling, monitor memory usage and consider limiting concurrent sessions

## License

MIT License
