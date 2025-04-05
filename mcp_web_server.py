from mcp.server.fastmcp import FastMCP, Context, Image

# Create an MCP server
mcp = FastMCP("Browser & Web Analysis MCP")

# Resource for home page
@mcp.resource("home://info")
def get_home_info() -> str:
    """Get information about this MCP server"""
    return """
    Custom MCP Server with browser access and web analysis capabilities
    
    Available functionality:
    - Browser control
    - Web crawling
    - HTML parsing
    - Screenshot capture
    - Web page analysis
    """

# Browser management tools
@mcp.tool()
def start_browser(headless: bool = True) -> dict:
    """Start a new browser session"""
    import os
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    
    try:
        # 현재 디렉토리에서 ChromeDriver 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chromedriver_path = os.path.join(current_dir, "chromedriver")
        
        # Chrome 옵션 설정
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
        
        # ChromeDriver 서비스 생성
        service = Service(executable_path=chromedriver_path)
        
        # 브라우저 시작
        driver = webdriver.Chrome(service=service, options=options)
        
        # 세션 ID 생성 및 저장
        session_id = f"session_{int(time.time())}"
        
        # 전역 레지스트리에 저장
        if not hasattr(start_browser, "sessions"):
            start_browser.sessions = {}
        
        start_browser.sessions[session_id] = driver
        
        return {
            "session_id": session_id,
            "status": "started",
            "browser_type": "Chrome"
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def navigate_to_url(session_id: str, url: str, ctx: Context = None) -> dict:
    """Navigate to a specific URL in a browser session"""
    import time
    
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    driver = start_browser.sessions[session_id]
    driver.get(url)
    
    # Wait for the page to load
    time.sleep(2)
    
    if ctx:
        ctx.info(f"Navigated to {url}")
    
    return {
        "title": driver.title,
        "current_url": driver.current_url
    }

@mcp.tool()
def take_screenshot(session_id: str, filename: str = None) -> dict:
    """Take a screenshot of the current browser view"""
    import os
    import time
    
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    # 현재 디렉토리 경로 가져오기
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 파일명이 지정되지 않은 경우 기본 파일명 생성
    if filename is None:
        filename = f"screenshot_{int(time.time())}.png"
    
    # 절대 경로로 변환
    screenshot_path = os.path.join(current_dir, filename)
    
    # 스크린샷 촬영
    driver = start_browser.sessions[session_id]
    screenshot_taken = driver.save_screenshot(screenshot_path)
    
    if not screenshot_taken:
        raise RuntimeError("Failed to take screenshot")
    
    return {
        "filename": filename,
        "absolute_path": screenshot_path,
        "status": "success"
    }

@mcp.tool()
def close_browser(session_id: str) -> dict:
    """Close a browser session"""
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    driver = start_browser.sessions[session_id]
    driver.quit()
    del start_browser.sessions[session_id]
    
    return {"session_id": session_id, "status": "closed"}

# Web crawling tools
@mcp.tool()
def crawl_url(url: str, headers: dict = None, params: dict = None, max_content_length: int = 5000, extract_selector: str = None) -> dict:
    """Crawl a URL using requests
    
    Parameters:
    - url: The URL to crawl
    - headers: Optional HTTP headers to send with the request
    - params: Optional query parameters
    - max_content_length: Maximum length of text content to return (default: 5000)
    - extract_selector: Optional CSS selector to extract specific elements only
    """
    import requests
    from bs4 import BeautifulSoup
    
    # Set default User-Agent if not provided
    if headers is None:
        headers = {}
    
    if "User-Agent" not in headers:
        headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    
    try:
        response = requests.get(url, headers=headers, params=params or {}, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e)
        }
    
    content_type = response.headers.get("Content-Type", "")
    full_text = response.text
    
    result = {
        "status_code": response.status_code,
        "content_type": content_type,
        "url": response.url,
        "content_length": len(full_text)
    }
    
    # If HTML content
    if "html" in content_type.lower():
        soup = BeautifulSoup(full_text, "html.parser")
        
        # Always extract basic page info
        result["title"] = soup.title.string if soup.title else ""
        
        # If specific selector is provided
        if extract_selector:
            elements = soup.select(extract_selector)
            
            if elements:
                # Extract content from matched elements
                extracted_content = "\n".join(str(el) for el in elements)
                result["text"] = extracted_content[:max_content_length]
                result["extracted_count"] = len(elements)
                if len(extracted_content) > max_content_length:
                    result["truncated"] = True
            else:
                # No elements found with selector - suggest common selectors
                result["text"] = f"No elements found matching selector: {extract_selector}"
                result["extracted_count"] = 0
                
                # Suggest common selectors and their element counts
                suggested_selectors = {
                    "article": len(soup.find_all("article")),
                    ".article": len(soup.select(".article")),
                    ".post": len(soup.select(".post")),
                    ".post-content": len(soup.select(".post-content")),
                    "main": len(soup.find_all("main")),
                    ".content": len(soup.select(".content"))
                }
                result["suggested_selectors"] = {sel: count for sel, count in suggested_selectors.items() if count > 0}
        else:
            # Return truncated text content
            result["text"] = full_text[:max_content_length]
            if len(full_text) > max_content_length:
                result["truncated"] = True
            
            # Suggest commonly used selectors for content extraction
            common_elements = {
                "Articles": len(soup.find_all("article")),
                "Main content": len(soup.find_all("main")),
                "Headings": len(soup.find_all(["h1", "h2", "h3"])),
                "Paragraphs": len(soup.find_all("p")),
                "Links": len(soup.find_all("a")),
                "Images": len(soup.find_all("img"))
            }
            result["page_elements"] = common_elements
    else:
        # For non-HTML content
        result["text"] = full_text[:max_content_length]
        if len(full_text) > max_content_length:
            result["truncated"] = True
    
    return result

@mcp.tool()
def find_selectors(html: str, content_keywords: list = None) -> dict:
    """Find useful CSS selectors in HTML content based on keywords
    
    Parameters:
    - html: HTML content to analyze
    - content_keywords: List of keywords to look for in content
    """
    from bs4 import BeautifulSoup
    import re
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Find common content containers
    common_containers = {
        "articles": [{"selector": f"article{cls}", "count": len(soup.select(f"article{cls}"))} 
                    for cls in ["", ".post", ".news", ".content"] if len(soup.select(f"article{cls}")) > 0],
        "main_content": [{"selector": sel, "count": len(soup.select(sel))} 
                        for sel in ["main", ".main", ".content", ".post-content", ".article-content"] 
                        if len(soup.select(sel)) > 0],
        "lists": [{"selector": sel, "count": len(soup.select(sel))} 
                for sel in [".list", "ul.posts", ".news-list", ".article-list"] 
                if len(soup.select(sel)) > 0]
    }
    
    # Find elements that might contain keywords
    keyword_matches = {}
    if content_keywords:
        for keyword in content_keywords:
            pattern = re.compile(keyword, re.IGNORECASE)
            matches = []
            
            # Look for elements containing the keyword in text or attributes
            for tag in soup.find_all(text=pattern):
                parent = tag.parent
                if parent.name:
                    # Get unique selector for this element
                    classes = parent.get('class', [])
                    if classes:
                        selector = f"{parent.name}.{'.'.join(classes)}"
                    else:
                        selector = parent.name
                    
                    matches.append({
                        "selector": selector,
                        "text_sample": tag.strip()[:100] if tag.strip() else "[No text]",
                        "element_type": parent.name
                    })
            
            if matches:
                keyword_matches[keyword] = matches[:5]  # Limit to 5 matches per keyword
    
    # Find components with specific roles
    content_components = {
        "headlines": [{"selector": sel, "count": len(soup.select(sel))} 
                     for sel in ["h1", "h2.title", ".headline", ".post-title"]
                     if len(soup.select(sel)) > 0],
        "text_content": [{"selector": sel, "count": len(soup.select(sel))} 
                        for sel in ["p", ".text", ".content p", "article p"]
                        if len(soup.select(sel)) > 0],
        "dates": [{"selector": sel, "count": len(soup.select(sel))} 
                 for sel in ["time", ".date", ".timestamp", ".published"]
                 if len(soup.select(sel)) > 0]
    }
    
    return {
        "common_containers": common_containers,
        "content_components": content_components,
        "keyword_matches": keyword_matches
    }

@mcp.tool()
def parse_html(html: str, selector: str = "", parser: str = "html.parser") -> dict:
    """Parse HTML content using BeautifulSoup"""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, parser)
    
    if not selector:
        # Return basic page info if no selector provided
        return {
            "title": soup.title.string if soup.title else "",
            "links": [link.get("href") for link in soup.find_all("a") if link.get("href")]
        }
    else:
        # Use the provided selector
        elements = soup.select(selector)
        results = []
        
        for element in elements:
            # Extract text and attributes
            element_data = {
                "text": element.get_text(strip=True),
                "html": str(element),
                "attrs": element.attrs
            }
            results.append(element_data)
        
        return {
            "count": len(results),
            "results": results
        }

@mcp.tool()
def execute_javascript(session_id: str, script: str) -> dict:
    """Execute JavaScript in the browser"""
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    driver = start_browser.sessions[session_id]
    result = driver.execute_script(script)
    
    # Handle non-serializable results
    try:
        import json
        json.dumps(result)
        serializable_result = result
    except (TypeError, OverflowError):
        serializable_result = str(result)
    
    return {"result": serializable_result}

# Add a prompt for browser automation
@mcp.prompt()
def browser_automation(task: str) -> str:
    return f"""
    Please automate this browser task: {task}
    
    You can use the following tools:
    1. start_browser() - Start a new browser session
    2. navigate_to_url(session_id, url) - Navigate to a specific URL
    3. take_screenshot(session_id, filename) - Take a screenshot
    4. execute_javascript(session_id, script) - Execute JavaScript
    5. close_browser(session_id) - Close the browser session
    
    Please provide a step-by-step plan for automating this task.
    """

# Add a prompt for web crawling
@mcp.prompt()
def web_crawler(target_url: str, data_to_extract: str) -> str:
    return f"""
    I need to crawl {target_url} and extract {data_to_extract}.
    
    Please help me use the available tools to accomplish this:
    1. crawl_url(url) - Fetch content from a URL
    2. parse_html(html, selector) - Extract data using CSS selectors
    
    Provide a step-by-step approach to extract the requested data.
    """

@mcp.tool()
def get_page_html(session_id: str, save_to_file: bool = False) -> dict:
    """Get the current page HTML source from a browser session
    
    Parameters:
    - session_id: Browser session ID
    - save_to_file: Whether to save HTML to a file (default: False)
    """
    import time
    import os
    
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    driver = start_browser.sessions[session_id]
    page_source = driver.page_source
    
    result = {
        "url": driver.current_url,
        "title": driver.title,
        "content_length": len(page_source)
    }
    
    # Save to file if requested
    if save_to_file:
        filename = f"page_source_{int(time.time())}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(page_source)
        result["saved_to_file"] = os.path.abspath(filename)
    
    # Truncate the HTML content to a reasonable size
    max_length = 10000  # 10KB
    if len(page_source) > max_length:
        result["html"] = page_source[:max_length] + "... [truncated]"
        result["truncated"] = True
    else:
        result["html"] = page_source
    
    return result

@mcp.tool()
def analyze_website_ui_ux(url: str, take_screenshot: bool = True, analyze_components: bool = True, analyze_colors: bool = True, analyze_typography: bool = True, analyze_layout: bool = True, wait_time: int = 5, analyze_advanced: bool = True) -> dict:
    """Analyze the UI/UX structure of a website for replication purposes
    
    Parameters:
    - url: The URL of the website to analyze
    - take_screenshot: Whether to take a screenshot of the website
    - analyze_components: Whether to analyze UI components
    - analyze_colors: Whether to analyze color scheme
    - analyze_typography: Whether to analyze typography
    - analyze_layout: Whether to analyze layout structure
    - wait_time: Time to wait for JavaScript to render (in seconds)
    - analyze_advanced: Whether to perform advanced analysis of layout and components
    """
    import time
    import os
    import requests
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import WebDriverException
    import re
    from PIL import Image
    from io import BytesIO
    import colorsys
    import numpy as np
    from collections import Counter
    
    result = {
        "url": url,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "success"
    }
    
    # Start browser session
    browser_session = start_browser(headless=False)
    if "status" in browser_session and browser_session["status"] == "error":
        return {
            "status": "error",
            "message": f"Failed to start browser: {browser_session['message']}"
        }
    
    session_id = browser_session["session_id"]
    
    try:
        # Navigate to the URL
        if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
            raise ValueError(f"Browser session '{session_id}' not found")
        
        driver = start_browser.sessions[session_id]
        driver.get(url)
        
        # Wait for page to load and JavaScript to execute
        time.sleep(wait_time)
        
        # Execute JavaScript to ensure all dynamic content is loaded
        driver.execute_script("""
            // Scroll down to trigger lazy loading
            window.scrollTo(0, document.body.scrollHeight / 2);
            return true;
        """)
        
        # Wait again for any lazy-loaded content
        time.sleep(2)
        
        # Take screenshot if requested
        if take_screenshot:
            screenshot_path = f"ui_analysis_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            result["screenshot"] = os.path.abspath(screenshot_path)
        
        # Get page HTML after JavaScript execution
        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")
        
        # Basic page information
        result["title"] = driver.title
        result["meta_tags"] = [{"name": tag.get("name", ""), "content": tag.get("content", "")} 
                              for tag in soup.find_all("meta") if tag.get("name") or tag.get("content")]
        
        # Perform advanced analysis if requested
        if analyze_advanced:
            # Analyze page layout structure
            layout_analysis = analyze_page_layout(session_id)
            result["advanced_layout_analysis"] = layout_analysis
            
            # Analyze component hierarchy
            component_hierarchy = analyze_component_hierarchy(session_id)
            result["component_hierarchy"] = component_hierarchy
            
            # Analyze responsive behavior
            responsive_analysis = analyze_responsive_behavior(session_id)
            result["responsive_analysis"] = responsive_analysis
        
        # Analyze layout structure (basic)
        if analyze_layout:
            layout = {
                "body_attributes": {attr: soup.body[attr] for attr in soup.body.attrs} if soup.body else {},
                "container_elements": []
            }
            
            # Find main containers
            containers = []
            for element in ["div", "main", "section", "header", "footer", "nav", "aside"]:
                for container in soup.find_all(element, class_=True):
                    class_name = " ".join(container.get("class", []))
                    if any(term in class_name.lower() for term in ["container", "wrapper", "layout", "main", "content"]):
                        containers.append({
                            "tag": container.name,
                            "class": class_name,
                            "id": container.get("id", ""),
                            "width": container.get("width", ""),
                            "children_count": len(list(container.children))
                        })
            
            layout["container_elements"] = containers[:10]  # Limit to top 10 containers
            
            # Analyze grid system
            grid_classes = []
            flex_classes = []
            
            for element in soup.find_all(class_=True):
                classes = " ".join(element.get("class", []))
                if any(grid_term in classes.lower() for grid_term in ["grid", "row", "col"]):
                    grid_classes.append(classes)
                if any(flex_term in classes.lower() for flex_term in ["flex", "display-flex"]):
                    flex_classes.append(classes)
            
            layout["grid_elements"] = Counter(grid_classes).most_common(10)
            layout["flex_elements"] = Counter(flex_classes).most_common(10)
            
            # Responsive design elements
            media_queries = []
            for style in soup.find_all("style"):
                if style.string:
                    queries = re.findall(r'@media\s+[^{]+{', style.string)
                    media_queries.extend(queries)
            
            # Look for viewport meta tag
            viewport = soup.find("meta", attrs={"name": "viewport"})
            
            layout["responsive_elements"] = {
                "media_queries": media_queries[:10],
                "viewport": viewport.get("content") if viewport else None
            }
            
            # Detect two-column layout patterns
            two_column_layout = False
            sidebar_position = "none"
            
            # Look for common sidebar patterns
            if soup.select("aside, .sidebar, #sidebar"):
                two_column_layout = True
                
                # Try to determine sidebar position
                for sidebar in soup.select("aside, .sidebar, #sidebar"):
                    # Check for position classes
                    sidebar_class = " ".join(sidebar.get("class", []))
                    if any(pos in sidebar_class.lower() for pos in ["left", "start"]):
                        sidebar_position = "left"
                        break
                    elif any(pos in sidebar_class.lower() for pos in ["right", "end"]):
                        sidebar_position = "right"
                    
                    # If no position class, try to infer from element order
                    if sidebar.find_next_sibling() and sidebar.find_next_sibling().select_one("main, .content, article"):
                        sidebar_position = "left"
                    elif sidebar.find_previous_sibling() and sidebar.find_previous_sibling().select_one("main, .content, article"):
                        sidebar_position = "right"
            
            layout["two_column_layout"] = {
                "detected": two_column_layout,
                "sidebar_position": sidebar_position
            }
            
            result["layout_analysis"] = layout
        
        # Analyze UI components
        if analyze_components:
            components = {}
            
            # Buttons
            buttons = []
            for button in soup.find_all("button"):
                buttons.append({
                    "text": button.text.strip(),
                    "class": " ".join(button.get("class", [])),
                    "id": button.get("id", ""),
                    "type": button.get("type", ""),
                    "disabled": button.has_attr("disabled")
                })
            
            # Also find a elements that look like buttons
            for a in soup.find_all("a", class_=True):
                classes = " ".join(a.get("class", []))
                if any(btn_term in classes.lower() for btn_term in ["btn", "button"]):
                    buttons.append({
                        "text": a.text.strip(),
                        "class": classes,
                        "id": a.get("id", ""),
                        "href": a.get("href", ""),
                        "element_type": "a"
                    })
            
            components["buttons"] = buttons[:20]  # Limit to top 20 buttons
            
            # Forms
            forms = []
            for form in soup.find_all("form"):
                inputs = []
                for input_field in form.find_all(["input", "select", "textarea"]):
                    inputs.append({
                        "type": input_field.get("type", input_field.name),
                        "name": input_field.get("name", ""),
                        "id": input_field.get("id", ""),
                        "placeholder": input_field.get("placeholder", ""),
                        "required": input_field.has_attr("required")
                    })
                
                forms.append({
                    "action": form.get("action", ""),
                    "method": form.get("method", ""),
                    "class": " ".join(form.get("class", [])),
                    "id": form.get("id", ""),
                    "inputs": inputs[:10]  # Limit to top 10 inputs per form
                })
            
            components["forms"] = forms[:5]  # Limit to top 5 forms
            
            # Navigation
            navs = []
            for nav in soup.find_all(["nav", "ul", "ol"]):
                if nav.name == "nav" or (nav.get("class") and any(nav_term in " ".join(nav.get("class", [])).lower() for nav_term in ["menu", "nav", "navigation"])):
                    links = []
                    for link in nav.find_all("a"):
                        links.append({
                            "text": link.text.strip(),
                            "href": link.get("href", ""),
                            "class": " ".join(link.get("class", []))
                        })
                    
                    navs.append({
                        "type": nav.name,
                        "class": " ".join(nav.get("class", [])),
                        "id": nav.get("id", ""),
                        "links": links[:10]  # Limit to top 10 links per nav
                    })
            
            components["navigation"] = navs[:3]  # Limit to top 3 navs
            
            # Cards/Panels
            cards = []
            for element in soup.find_all(class_=True):
                classes = " ".join(element.get("class", []))
                if any(card_term in classes.lower() for card_term in ["card", "panel", "box", "tile"]):
                    card_content = {
                        "tag": element.name,
                        "class": classes,
                        "id": element.get("id", ""),
                        "heading": element.find(["h1", "h2", "h3", "h4", "h5", "h6"]).text.strip() if element.find(["h1", "h2", "h3", "h4", "h5", "h6"]) else "",
                        "has_image": bool(element.find("img")),
                        "has_button": bool(element.find(["button", "a"]))
                    }
                    cards.append(card_content)
            
            components["cards"] = cards[:10]  # Limit to top 10 cards
            
            # Find sidebar elements (new)
            sidebar_elements = []
            sidebar_selectors = ["aside", ".sidebar", "#sidebar", ".widget-area", ".right-sidebar", ".left-sidebar"]
            
            for selector in sidebar_selectors:
                for element in soup.select(selector):
                    # Look for common sidebar content patterns
                    sidebar_element = {
                        "selector": selector,
                        "id": element.get("id", ""),
                        "class": " ".join(element.get("class", [])),
                        "contains": []
                    }
                    
                    # Check for search form
                    if element.select("form input[type=search], form input[type=text]"):
                        sidebar_element["contains"].append("search")
                    
                    # Check for popular/recent content
                    headings = element.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
                    for heading in headings:
                        heading_text = heading.text.lower()
                        if any(term in heading_text for term in ["popular", "recent", "trending", "featured"]):
                            sidebar_element["contains"].append("popular_content")
                    
                    # Check for category/tag lists
                    if element.select("ul li a, .tag, .category"):
                        sidebar_element["contains"].append("categories_or_tags")
                    
                    sidebar_elements.append(sidebar_element)
            
            components["sidebar_elements"] = sidebar_elements
            
            result["component_analysis"] = components
        
        # Analyze color scheme
        if analyze_colors and take_screenshot:
            try:
                img = Image.open(result["screenshot"])
                img = img.resize((150, 150))  # Resize for faster processing
                pixels = np.array(img)
                pixels = pixels.reshape(-1, 3)
                
                # Get the most common colors
                colors = Counter(tuple(pixel) for pixel in pixels)
                most_common_colors = colors.most_common(10)
                
                # Convert RGB to hex and calculate HSL
                color_analysis = []
                for color, count in most_common_colors:
                    r, g, b = color
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"
                    
                    # Convert RGB to HSL
                    r, g, b = r/255.0, g/255.0, b/255.0
                    h, l, s = colorsys.rgb_to_hls(r, g, b)
                    h = int(h * 360)
                    s = int(s * 100)
                    l = int(l * 100)
                    
                    color_type = "unknown"
                    if s < 10:
                        if l < 20:
                            color_type = "black"
                        elif l > 80:
                            color_type = "white"
                        else:
                            color_type = "gray"
                    else:
                        if h < 30 or h > 330:
                            color_type = "red"
                        elif h < 90:
                            color_type = "yellow"
                        elif h < 150:
                            color_type = "green"
                        elif h < 210:
                            color_type = "cyan"
                        elif h < 270:
                            color_type = "blue"
                        elif h < 330:
                            color_type = "magenta"
                    
                    color_analysis.append({
                        "hex": hex_color,
                        "rgb": color,
                        "hsl": {"h": h, "s": s, "l": l},
                        "type": color_type,
                        "frequency": count / len(pixels)
                    })
                
                result["color_analysis"] = color_analysis
            except Exception as e:
                result["color_analysis"] = {"error": str(e)}
        
        # Analyze typography
        if analyze_typography:
            typography = {}
            
            # Get all font families
            font_families = []
            for style in soup.find_all("style"):
                if style.string:
                    families = re.findall(r'font-family:\s*([^;}]+)[;}]', style.string)
                    font_families.extend(families)
            
            # Get font sizes
            font_sizes = []
            for element in soup.find_all():
                style = element.get("style", "")
                if "font-size" in style:
                    size = re.search(r'font-size:\s*([^;}]+)[;}]', style)
                    if size:
                        font_sizes.append(size.group(1))
            
            # Analyze headings
            headings = {}
            for level in range(1, 7):
                heading_tag = f"h{level}"
                tags = soup.find_all(heading_tag)
                if tags:
                    samples = []
                    for tag in tags[:3]:  # Get samples of the first 3 headings
                        samples.append({
                            "text": tag.text.strip(),
                            "class": " ".join(tag.get("class", [])),
                            "id": tag.get("id", "")
                        })
                    
                    headings[heading_tag] = {
                        "count": len(tags),
                        "samples": samples
                    }
            
            # Find font-related CSS classes
            font_classes = []
            for element in soup.find_all(class_=True):
                classes = " ".join(element.get("class", []))
                if any(font_term in classes.lower() for font_term in ["font", "text", "type"]):
                    font_classes.append(classes)
            
            typography["font_families"] = font_families[:10]
            typography["font_sizes"] = font_sizes[:10]
            typography["headings"] = headings
            typography["font_classes"] = Counter(font_classes).most_common(10)
            
            result["typography_analysis"] = typography
        
        # General UX patterns
        ux_patterns = {
            "has_cookie_consent": bool(re.search(r'cookie|consent|gdpr', page_html, re.IGNORECASE)),
            "has_login_form": bool(soup.find("form", id=re.compile(r"login", re.IGNORECASE)) or 
                                  soup.find("form", class_=re.compile(r"login", re.IGNORECASE))),
            "has_search": bool(soup.find("input", attrs={"type": "search"}) or 
                              soup.find("form", id=re.compile(r"search", re.IGNORECASE)) or
                              soup.find("form", class_=re.compile(r"search", re.IGNORECASE))),
            "has_social_sharing": bool(re.search(r'share|twitter|facebook|linkedin|social', page_html, re.IGNORECASE)),
            "has_newsletter_signup": bool(re.search(r'newsletter|subscribe|signup', page_html, re.IGNORECASE)),
            "has_breadcrumbs": bool(soup.find(class_=re.compile(r"breadcrumb", re.IGNORECASE))),
            "has_pagination": bool(soup.find(class_=re.compile(r"pagination", re.IGNORECASE))),
            "has_dropdown_menu": bool(soup.find(class_=re.compile(r"dropdown", re.IGNORECASE))),
            "has_accordion": bool(soup.find(class_=re.compile(r"accordion", re.IGNORECASE))),
            "has_tabs": bool(soup.find(class_=re.compile(r"tab", re.IGNORECASE)) and not 
                            soup.find(class_=re.compile(r"table", re.IGNORECASE)))
        }
        
        result["ux_patterns"] = ux_patterns
        
        # Generate page structure report
        structure_summary = {
            "has_sidebar": bool(soup.select("aside, .sidebar, #sidebar")),
            "has_search_in_sidebar": bool(soup.select("aside form input[type=search], .sidebar form input[type=search]")),
            "search_position": "unknown"
        }
        
        # Determine search position
        search_elements = soup.select("input[type=search], form input[placeholder*=search]")
        if search_elements:
            for search in search_elements:
                # Check if search is in sidebar
                parents = list(search.parents)
                for parent in parents:
                    if parent.name == "aside" or (parent.get("class") and any(cls in ["sidebar", "widget-area"] for cls in parent.get("class", []))):
                        structure_summary["search_position"] = "sidebar"
                        break
                
                # If not found in sidebar, check if in header
                if structure_summary["search_position"] == "unknown":
                    for parent in parents:
                        if parent.name == "header" or (parent.get("class") and "header" in " ".join(parent.get("class", []))):
                            structure_summary["search_position"] = "header"
                            break
        
        result["page_structure"] = structure_summary
        
    except Exception as e:
        result = {
            "status": "error",
            "message": str(e)
        }
    
    finally:
        # Close the browser session
        try:
            close_browser(session_id)
        except:
            pass
    
    return result

@mcp.tool()
def analyze_page_layout(session_id: str) -> dict:
    """Analyze the page layout structure after JavaScript rendering
    
    Performs detailed analysis of the layout structure including:
    - Multi-column layouts
    - Sidebar detection
    - Main content area detection
    - Hierarchical component structure
    
    Parameters:
    - session_id: Browser session ID
    """
    import os
    from bs4 import BeautifulSoup
    from collections import Counter
    
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    driver = start_browser.sessions[session_id]
    
    # Execute JavaScript to get computed styles and layout information
    layout_script = """
    function getElementLayout(element) {
        const style = window.getComputedStyle(element);
        return {
            display: style.display,
            position: style.position,
            float: style.float,
            width: style.width,
            height: style.height,
            flexDirection: style.flexDirection,
            gridTemplateColumns: style.gridTemplateColumns,
            gridTemplateRows: style.gridTemplateRows
        };
    }
    
    function analyzeLayout() {
        // Find potential layout containers
        const containers = [];
        const bodyChildren = Array.from(document.body.children);
        
        // Look for main layout containers
        const layoutElements = document.querySelectorAll('main, .main, .container, .content, .layout, .wrapper, .page, #root, #app');
        layoutElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            const computed = getElementLayout(element);
            
            containers.push({
                tag: element.tagName.toLowerCase(),
                id: element.id || '',
                classes: Array.from(element.classList).join(' '),
                width: rect.width,
                height: rect.height,
                layout: computed,
                children: element.children.length,
                path: getElementPath(element)
            });
        });
        
        // Detect multi-column layouts
        const multiColumnLayouts = [];
        document.querySelectorAll('*').forEach(el => {
            const style = window.getComputedStyle(el);
            
            // Check for grid or flex layouts that might represent multi-column
            if ((style.display === 'grid' && style.gridTemplateColumns.includes(' ')) || 
                (style.display === 'flex' && style.flexDirection.includes('row') && el.children.length > 1)) {
                
                // Check if children have significant width
                let hasColumns = false;
                let columnWidths = [];
                
                Array.from(el.children).forEach(child => {
                    const childRect = child.getBoundingClientRect();
                    if (childRect.width > 200) { // Minimum width for a "column"
                        hasColumns = true;
                        columnWidths.push(childRect.width);
                    }
                });
                
                if (hasColumns) {
                    multiColumnLayouts.push({
                        element: getElementPath(el),
                        display: style.display,
                        columnCount: el.children.length,
                        columnWidths: columnWidths
                    });
                }
            }
        });
        
        // Detect sidebar layouts
        const sidebarLayouts = [];
        multiColumnLayouts.forEach(layout => {
            // If there are at least 2 columns and one is significantly narrower
            if (layout.columnWidths.length >= 2) {
                layout.columnWidths.sort((a, b) => a - b);
                
                // If smallest column is less than 40% of largest, it might be a sidebar
                if (layout.columnWidths[0] < layout.columnWidths[layout.columnWidths.length - 1] * 0.4) {
                    sidebarLayouts.push({
                        element: layout.element,
                        display: layout.display,
                        sidebarWidth: layout.columnWidths[0],
                        mainContentWidth: layout.columnWidths[layout.columnWidths.length - 1]
                    });
                }
            }
        });
        
        // Helper function to get element path
        function getElementPath(element) {
            let path = '';
            while (element && element.tagName) {
                let selector = element.tagName.toLowerCase();
                if (element.id) {
                    selector += '#' + element.id;
                } else {
                    let classes = Array.from(element.classList).join('.');
                    if (classes) {
                        selector += '.' + classes;
                    }
                }
                path = selector + (path ? ' > ' + path : '');
                element = element.parentElement;
            }
            return path;
        }
        
        return {
            containers: containers,
            multiColumnLayouts: multiColumnLayouts,
            sidebarLayouts: sidebarLayouts
        };
    }
    
    return analyzeLayout();
    """
    
    # Execute the layout analysis script
    layout_data = driver.execute_script(layout_script)
    
    # Get the page HTML for further analysis
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, "html.parser")
    
    # Analyze content areas
    content_areas = []
    potential_content_selectors = [
        "main", "#content", ".content", "article", ".post", 
        ".main-content", "#main-content", ".page-content"
    ]
    
    for selector in potential_content_selectors:
        elements = soup.select(selector)
        for element in elements:
            text_length = len(element.get_text(strip=True))
            if text_length > 500:  # Assume significant content has some minimum length
                content_areas.append({
                    "selector": selector,
                    "text_length": text_length,
                    "children_count": len(list(element.children))
                })
    
    # Analyze sidebar areas
    sidebar_areas = []
    potential_sidebar_selectors = [
        "aside", ".sidebar", "#sidebar", ".widget-area", ".right-sidebar", 
        ".left-sidebar", ".side-content"
    ]
    
    for selector in potential_sidebar_selectors:
        elements = soup.select(selector)
        for element in elements:
            sidebar_areas.append({
                "selector": selector,
                "text_length": len(element.get_text(strip=True)),
                "children_count": len(list(element.children))
            })
    
    # Determine overall layout type
    layout_type = "single-column"
    if layout_data["sidebarLayouts"] and len(layout_data["sidebarLayouts"]) > 0:
        layout_type = "sidebar-layout"
    elif layout_data["multiColumnLayouts"] and len(layout_data["multiColumnLayouts"]) > 0:
        layout_type = "multi-column"
    
    result = {
        "layout_type": layout_type,
        "containers": layout_data["containers"],
        "multi_column_layouts": layout_data["multiColumnLayouts"],
        "sidebar_layouts": layout_data["sidebarLayouts"],
        "content_areas": content_areas,
        "sidebar_areas": sidebar_areas
    }
    
    return result

@mcp.tool()
def analyze_component_hierarchy(session_id: str) -> dict:
    """Analyze the component hierarchy and relationships in a rendered page
    
    Examines parent-child relationships between UI components to understand
    the page structure and component nesting.
    
    Parameters:
    - session_id: Browser session ID
    """
    from bs4 import BeautifulSoup
    
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    driver = start_browser.sessions[session_id]
    
    # Execute JavaScript to analyze component hierarchy
    hierarchy_script = """
    function analyzeComponentHierarchy() {
        // Identify important structural components
        const components = [];
        
        // Common component selectors
        const componentSelectors = [
            'header', 'nav', 'main', 'article', 'section', 'aside', 'footer',
            '.card', '.panel', '.widget', '.sidebar', '.menu', '.navbar',
            '.container', '.wrapper', '.layout', '.grid', '.row',
            '#header', '#footer', '#main', '#content', '#sidebar'
        ];
        
        // Get all elements matching our component selectors
        const elements = [];
        componentSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                elements.push(el);
            });
        });
        
        // Remove duplicates (an element might match multiple selectors)
        const uniqueElements = [...new Set(elements)];
        
        // Analyze each unique element
        uniqueElements.forEach(element => {
            // Skip tiny elements that are likely not structural
            const rect = element.getBoundingClientRect();
            if (rect.width < 50 || rect.height < 50) return;
            
            // Create component info
            const component = {
                type: element.tagName.toLowerCase(),
                classes: Array.from(element.classList).join(' '),
                id: element.id || '',
                children: getChildComponents(element),
                size: {
                    width: rect.width,
                    height: rect.height
                },
                position: {
                    top: rect.top + window.scrollY,
                    left: rect.left + window.scrollX
                },
                isVisible: isElementVisible(element),
                textContent: element.innerText.trim().substring(0, 100) + (element.innerText.length > 100 ? '...' : '')
            };
            
            components.push(component);
        });
        
        // Get child components
        function getChildComponents(element) {
            const children = [];
            
            for (const child of element.children) {
                // Skip text nodes and tiny elements
                if (child.nodeType !== 1) continue;
                
                const rect = child.getBoundingClientRect();
                if (rect.width < 20 || rect.height < 20) continue;
                
                children.push({
                    type: child.tagName.toLowerCase(),
                    classes: Array.from(child.classList).join(' '),
                    id: child.id || '',
                    size: {
                        width: rect.width,
                        height: rect.height
                    },
                    hasChildren: child.children.length > 0
                });
            }
            
            return children;
        }
        
        // Check if element is visible
        function isElementVisible(element) {
            const style = window.getComputedStyle(element);
            return style.display !== 'none' && 
                   style.visibility !== 'hidden' && 
                   style.opacity !== '0';
        }
        
        // Analyze page regions
        const viewportHeight = window.innerHeight;
        const pageHeight = document.body.scrollHeight;
        
        const regions = {
            header: findComponentsInRegion(0, viewportHeight * 0.3),
            content: findComponentsInRegion(viewportHeight * 0.2, viewportHeight * 0.8),
            footer: findComponentsInRegion(pageHeight - viewportHeight * 0.3, pageHeight)
        };
        
        function findComponentsInRegion(startY, endY) {
            return components.filter(comp => 
                comp.position.top >= startY && 
                comp.position.top <= endY
            ).map(comp => ({
                type: comp.type,
                id: comp.id,
                classes: comp.classes
            }));
        }
        
        return {
            components: components,
            regions: regions,
            totalComponents: components.length
        };
    }
    
    return analyzeComponentHierarchy();
    """
    
    # Execute the hierarchy analysis script
    hierarchy_data = driver.execute_script(hierarchy_script)
    
    # Get the page HTML for further analysis
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, "html.parser")
    
    # Analyze top-level structure
    top_level_elements = []
    if soup.body:
        for child in soup.body.children:
            if child.name and not child.name.startswith('#'):
                element_info = {
                    "tag": child.name,
                    "id": child.get('id', ''),
                    "classes": ' '.join(child.get('class', [])),
                    "children_count": len([c for c in child.children if c.name]),
                    "text_length": len(child.get_text(strip=True))
                }
                top_level_elements.append(element_info)
    
    # Analyze nested component patterns
    nested_patterns = []
    common_patterns = [
        ("header", "nav"),
        ("nav", "ul", "li", "a"),
        ("main", "article"),
        ("article", "header", "main", "footer"),
        ("section", "article"),
        (".container", ".row", ".col"),
        (".card", ".card-header", ".card-body")
    ]
    
    for pattern in common_patterns:
        found = False
        # Check for pattern match in the DOM
        if len(pattern) > 1:
            # Look for first element in pattern
            elements = soup.find_all(pattern[0]) if not pattern[0].startswith('.') else soup.select(pattern[0])
            
            for element in elements:
                # Check if this element contains the complete pattern
                current = element
                pattern_matches = [current]
                
                for i in range(1, len(pattern)):
                    # Look for child matching the next pattern element
                    next_selector = pattern[i]
                    if next_selector.startswith('.'):
                        next_elements = current.select(next_selector)
                    else:
                        next_elements = current.find_all(next_selector, recursive=False)
                    
                    if next_elements:
                        current = next_elements[0]
                        pattern_matches.append(current)
                    else:
                        break
                
                if len(pattern_matches) == len(pattern):
                    found = True
                    nested_patterns.append({
                        "pattern": ' > '.join(pattern),
                        "found": True,
                        "sample": ' > '.join([f"{el.name}{'.'+el.get('class', ['_'])[0] if el.get('class') else ''}" for el in pattern_matches])
                    })
                    break
        
        if not found:
            nested_patterns.append({
                "pattern": ' > '.join(pattern),
                "found": False
            })
    
    result = {
        "component_hierarchy": hierarchy_data["components"][:15],  # Limit to top 15 components
        "page_regions": hierarchy_data["regions"],
        "top_level_elements": top_level_elements,
        "nested_patterns": nested_patterns,
        "total_components": hierarchy_data["totalComponents"]
    }
    
    return result

@mcp.tool()
def analyze_responsive_behavior(session_id: str) -> dict:
    """Analyze how a website behaves at different screen sizes
    
    Tests the page at multiple viewport widths to determine:
    - Breakpoints where layout changes
    - Mobile vs desktop behavior
    - Responsive design patterns used
    
    Parameters:
    - session_id: Browser session ID
    """
    import time
    from bs4 import BeautifulSoup
    
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    driver = start_browser.sessions[session_id]
    
    # Define viewport sizes to test
    viewports = [
        {"name": "mobile", "width": 375, "height": 667},
        {"name": "tablet", "width": 768, "height": 1024},
        {"name": "laptop", "width": 1366, "height": 768},
        {"name": "desktop", "width": 1920, "height": 1080}
    ]
    
    # JavaScript to analyze layout changes
    layout_script = """
    function analyzeCurrentLayout() {
        const elements = document.querySelectorAll('body *');
        const layoutInfo = {
            windowWidth: window.innerWidth,
            windowHeight: window.innerHeight,
            elementsVisible: 0,
            elementsHidden: 0,
            menuState: 'unknown',
            layoutType: 'unknown'
        };
        
        // Count visible/hidden elements
        elements.forEach(el => {
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                layoutInfo.elementsHidden++;
            } else {
                layoutInfo.elementsVisible++;
            }
        });
        
        // Detect menu state
        const navMenu = document.querySelector('nav, .nav, .navbar, .menu, header ul');
        if (navMenu) {
            const menuStyle = window.getComputedStyle(navMenu);
            const isHamburger = document.querySelector('.hamburger, .menu-toggle, .navbar-toggler, [aria-label="menu"], [aria-label="toggle menu"]');
            
            if (isHamburger && window.getComputedStyle(isHamburger).display !== 'none') {
                layoutInfo.menuState = 'hamburger';
            } else if (menuStyle.display !== 'none') {
                layoutInfo.menuState = 'expanded';
            }
        }
        
        // Detect layout type
        const body = document.body;
        const bodyWidth = body.offsetWidth;
        
        // Look for signs of multi-column layout
        const hasGrid = document.querySelector('[class*="grid"], [class*="row"], [style*="grid"]');
        const hasSidebar = document.querySelector('aside, .sidebar, #sidebar');
        
        if (bodyWidth <= 768) {
            layoutInfo.layoutType = 'single-column-mobile';
        } else if (hasGrid && hasSidebar) {
            layoutInfo.layoutType = 'multi-column-with-sidebar';
        } else if (hasGrid) {
            layoutInfo.layoutType = 'multi-column';
        } else if (hasSidebar) {
            layoutInfo.layoutType = 'content-with-sidebar';
        } else {
            layoutInfo.layoutType = 'single-column';
        }
        
        return layoutInfo;
    }
    
    return analyzeCurrentLayout();
    """
    
    # Store layout information for each viewport
    layouts = []
    current_url = driver.current_url
    
    # Test each viewport size
    for viewport in viewports:
        # Resize the browser window
        driver.set_window_size(viewport["width"], viewport["height"])
        
        # Give the page time to adjust
        time.sleep(2)
        
        # Execute analysis script
        layout_data = driver.execute_script(layout_script)
        
        # Take a screenshot at this viewport
        screenshot_name = f"viewport_{viewport['name']}_{int(time.time())}.png"
        driver.save_screenshot(screenshot_name)
        
        # Add viewport data to results
        viewport_result = {
            "viewport": viewport,
            "layout_info": layout_data,
            "screenshot": screenshot_name
        }
        
        layouts.append(viewport_result)
    
    # Analyze breakpoints
    breakpoints = []
    for i in range(1, len(layouts)):
        prev = layouts[i-1]
        curr = layouts[i]
        
        # Check if layout type changed
        if prev["layout_info"]["layoutType"] != curr["layout_info"]["layoutType"] or \
           prev["layout_info"]["menuState"] != curr["layout_info"]["menuState"]:
            
            breakpoint = {
                "lower_width": prev["viewport"]["width"],
                "upper_width": curr["viewport"]["width"],
                "changes": []
            }
            
            if prev["layout_info"]["layoutType"] != curr["layout_info"]["layoutType"]:
                breakpoint["changes"].append({
                    "property": "layoutType",
                    "from": prev["layout_info"]["layoutType"],
                    "to": curr["layout_info"]["layoutType"]
                })
            
            if prev["layout_info"]["menuState"] != curr["layout_info"]["menuState"]:
                breakpoint["changes"].append({
                    "property": "menuState",
                    "from": prev["layout_info"]["menuState"],
                    "to": curr["layout_info"]["menuState"]
                })
            
            breakpoints.append(breakpoint)
    
    # Detect CSS media query breakpoints
    driver.set_window_size(viewports[-1]["width"], viewports[-1]["height"])
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, "html.parser")
    
    media_queries = []
    for style in soup.find_all("style"):
        if style.string:
            import re
            queries = re.findall(r'@media\s+([^{]+){', style.string)
            for query in queries:
                # Extract width information
                width_match = re.search(r'(min-width|max-width):\s*(\d+)(px|rem|em)', query)
                if width_match:
                    media_queries.append({
                        "type": width_match.group(1),
                        "value": width_match.group(2),
                        "unit": width_match.group(3),
                        "full_query": query.strip()
                    })
    
    result = {
        "viewport_layouts": layouts,
        "detected_breakpoints": breakpoints,
        "media_queries": media_queries[:10],  # Limit to top 10 media queries
        "is_responsive": len(breakpoints) > 0 or len(media_queries) > 0
    }
    
    return result

@mcp.tool()
def click_element_and_wait(session_id: str, selector: str, wait_time: int = 5, take_screenshot: bool = True) -> dict:
    """Click on a specific element and wait for the new page to load
    
    Parameters:
    - session_id: Browser session ID
    - selector: CSS selector for the element to click
    - wait_time: Time to wait for the page to load in seconds (default: 5)
    - take_screenshot: Whether to take a screenshot after navigation (default: True)
    """
    import time
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    driver = start_browser.sessions[session_id]
    original_url = driver.current_url
    
    result = {
        "status": "success",
        "original_url": original_url
    }
    
    try:
        # Try to find element with WebDriverWait to ensure the page is ready
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        
        # Store information about the clicked element
        result["element_info"] = {
            "tag_name": element.tag_name,
            "text": element.text.strip() if element.text else "[No text]",
            "attributes": {attr: element.get_attribute(attr) for attr in ["id", "class", "href", "src"] if element.get_attribute(attr)}
        }
        
        # Click the element
        element.click()
        
        # Wait for the page to change and load
        wait_started = time.time()
        
        # First check if URL changed (for link clicks)
        try:
            WebDriverWait(driver, wait_time).until(EC.url_changes(original_url))
            result["navigation_type"] = "url_change"
        except TimeoutException:
            # If URL didn't change, we might be dealing with an in-page action
            # Wait for the fixed amount provided
            time.sleep(wait_time)
            result["navigation_type"] = "in_page_action"
        
        # Additional wait time to ensure the page has fully loaded
        # Use document.readyState to check if the page is completely loaded
        wait_script = """
        return document.readyState === 'complete';
        """
        
        try:
            WebDriverWait(driver, wait_time).until(lambda d: d.execute_script(wait_script))
        except TimeoutException:
            result["warning"] = "Page might not have fully loaded within the wait time"
        
        # Record the wait time
        result["wait_duration"] = time.time() - wait_started
        
        # Get information about the new page
        result["new_url"] = driver.current_url
        result["new_title"] = driver.title
        result["url_changed"] = original_url != driver.current_url
        
        # Take a screenshot if requested
        if take_screenshot:
            screenshot_name = f"after_click_{int(time.time())}.png"
            driver.save_screenshot(screenshot_name)
            result["screenshot"] = screenshot_name
        
    except NoSuchElementException:
        result = {
            "status": "error",
            "message": f"Element not found with selector: {selector}",
            "current_url": driver.current_url
        }
    except Exception as e:
        result = {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__,
            "current_url": driver.current_url
        }
    
    return result

@mcp.tool()
def find_clickable_elements(session_id: str, element_types: list = None) -> dict:
    """Find all clickable elements on the current page
    
    Parameters:
    - session_id: Browser session ID
    - element_types: List of element types to look for (default: links, buttons, and inputs)
    """
    import time
    from bs4 import BeautifulSoup
    
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    driver = start_browser.sessions[session_id]
    
    # Set default element types if none provided
    if element_types is None:
        element_types = ["links", "buttons", "inputs", "menu_items"]
    
    # Get page HTML
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, "html.parser")
    
    result = {
        "url": driver.current_url,
        "title": driver.title,
        "clickable_elements": {}
    }
    
    # Execute JavaScript to find elements that are visible and clickable
    clickable_script = """
    function getClickableElements() {
        const clickableElements = [];
        
        // Check if element is visible and clickable
        function isElementClickable(element) {
            if (!element) return false;
            
            const rect = element.getBoundingClientRect();
            const style = window.getComputedStyle(element);
            
            // Element must be visible
            if (rect.width === 0 || rect.height === 0) return false;
            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
            
            // Element must be in viewport
            if (rect.bottom < 0 || rect.top > window.innerHeight || 
                rect.right < 0 || rect.left > window.innerWidth) return false;
            
            return true;
        }
        
        // Get unique selector for an element
        function getElementSelector(element) {
            if (element.id) return `#${element.id}`;
            
            if (element.classList && element.classList.length > 0) {
                const classSelector = `.${Array.from(element.classList).join('.')}`;
                // Check if this selector is unique
                if (document.querySelectorAll(classSelector).length === 1) {
                    return classSelector;
                }
            }
            
            // Try with tag and class
            if (element.classList && element.classList.length > 0) {
                const tagClassSelector = `${element.tagName.toLowerCase()}.${Array.from(element.classList).join('.')}`;
                if (document.querySelectorAll(tagClassSelector).length === 1) {
                    return tagClassSelector;
                }
            }
            
            // If we have a parent with ID, use that
            let parent = element.parentElement;
            while (parent) {
                if (parent.id) {
                    return `#${parent.id} > ${element.tagName.toLowerCase()}`;
                }
                parent = parent.parentElement;
            }
            
            // Last resort: find position among siblings
            let index = 0;
            let sibling = element;
            while (sibling.previousElementSibling) {
                sibling = sibling.previousElementSibling;
                index++;
            }
            
            return `${element.tagName.toLowerCase()}:nth-child(${index + 1})`;
        }
        
        // Find all potentially clickable elements
        document.querySelectorAll('a, button, input[type=submit], input[type=button], [role=button], [onclick], .menu-item, .nav-item, .dropdown-item').forEach(element => {
            if (isElementClickable(element)) {
                clickableElements.push({
                    tagName: element.tagName.toLowerCase(),
                    text: element.innerText.trim().substring(0, 100) || '[No text]',
                    selector: getElementSelector(element),
                    attributes: {
                        id: element.id || '',
                        class: element.className || '',
                        href: element.href || '',
                        role: element.getAttribute('role') || '',
                        type: element.type || ''
                    },
                    position: {
                        x: element.getBoundingClientRect().left,
                        y: element.getBoundingClientRect().top
                    },
                    dimensions: {
                        width: element.getBoundingClientRect().width,
                        height: element.getBoundingClientRect().height
                    }
                });
            }
        });
        
        return clickableElements;
    }
    
    return getClickableElements();
    """
    
    clickable_elements = driver.execute_script(clickable_script)
    
    # Organize results by element type
    links = []
    buttons = []
    inputs = []
    menu_items = []
    
    for element in clickable_elements:
        element_info = {
            "text": element["text"],
            "selector": element["selector"],
            "id": element["attributes"]["id"],
            "class": element["attributes"]["class"],
            "position": element["position"]
        }
        
        # Categorize by element type
        if element["tagName"] == "a":
            element_info["href"] = element["attributes"]["href"]
            links.append(element_info)
        elif element["tagName"] == "button" or element["attributes"]["role"] == "button":
            element_info["type"] = element["attributes"]["type"]
            buttons.append(element_info)
        elif element["tagName"].startswith("input"):
            element_info["type"] = element["attributes"]["type"]
            inputs.append(element_info)
        elif "menu-item" in element["attributes"]["class"] or "nav-item" in element["attributes"]["class"] or "dropdown-item" in element["attributes"]["class"]:
            menu_items.append(element_info)
    
    # Add categories based on requested element types
    if "links" in element_types:
        result["clickable_elements"]["links"] = links
    if "buttons" in element_types:
        result["clickable_elements"]["buttons"] = buttons
    if "inputs" in element_types:
        result["clickable_elements"]["inputs"] = inputs
    if "menu_items" in element_types:
        result["clickable_elements"]["menu_items"] = menu_items
    
    # Add total counts
    result["total_clickable"] = len(clickable_elements)
    result["counts"] = {
        "links": len(links),
        "buttons": len(buttons),
        "inputs": len(inputs),
        "menu_items": len(menu_items)
    }
    
    return result

@mcp.tool()
def navigate_and_analyze(session_id: str, selector: str, wait_time: int = 5, analysis_type: str = "basic") -> dict:
    """Click on a specific element, wait for the new page to load, and then analyze the page structure
    
    Parameters:
    - session_id: Browser session ID
    - selector: CSS selector for the element to click
    - wait_time: Time to wait for the page to load in seconds (default: 5)
    - analysis_type: Type of analysis to perform after navigation ("basic", "layout", "components", "full")
    """
    # Click element and wait for navigation
    click_result = click_element_and_wait(session_id, selector, wait_time)
    
    if click_result["status"] == "error":
        return {
            "status": "error",
            "message": click_result["message"],
            "navigation_failed": True
        }
    
    # Analyze the new page based on analysis type
    analysis_result = {}
    
    if analysis_type == "layout" or analysis_type == "full":
        layout_analysis = analyze_page_layout(session_id)
        analysis_result["layout_analysis"] = layout_analysis
    
    if analysis_type == "components" or analysis_type == "full":
        component_analysis = analyze_component_hierarchy(session_id)
        analysis_result["component_analysis"] = component_analysis
    
    if analysis_type == "full":
        responsive_analysis = analyze_responsive_behavior(session_id)
        analysis_result["responsive_analysis"] = responsive_analysis
    
    # For basic analysis or as part of any analysis, get page info and clickable elements
    if not hasattr(start_browser, "sessions") or session_id not in start_browser.sessions:
        raise ValueError(f"Browser session '{session_id}' not found")
    
    driver = start_browser.sessions[session_id]
    
    # Basic page information
    analysis_result["page_info"] = {
        "url": driver.current_url,
        "title": driver.title,
        "previous_url": click_result["original_url"]
    }
    
    # Find clickable elements on the new page
    clickable_elements = find_clickable_elements(session_id)
    analysis_result["clickable_elements"] = clickable_elements
    
    # Compile final result
    result = {
        "status": "success",
        "navigation": {
            "from_url": click_result["original_url"],
            "to_url": click_result["new_url"],
            "clicked_element": click_result["element_info"]
        },
        "analysis": analysis_result
    }
    
    return result

@mcp.tool()
def deep_web_search(query: str, max_pages: int = 5, search_engine: str = "google", depth: int = 2, extract_relevant_content: bool = True) -> dict:
    """Perform a deep search on the web for a specific query, exploring multiple pages to find relevant information
    
    Parameters:
    - query: The search query to find information for
    - max_pages: Maximum number of pages to explore from search results (default: 5)
    - search_engine: Search engine to use (google, bing, ddg) (default: google)
    - depth: How deep to navigate from each result page (0 = search results only, 1 = visit result pages, 2 = follow links from result pages) (default: 2)
    - extract_relevant_content: Whether to extract and summarize content relevant to the query (default: True)
    """
    import time
    import re
    import urllib.parse
    from bs4 import BeautifulSoup
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
    
    # Initialize browser
    browser_session = start_browser(headless=True)
    session_id = browser_session["session_id"]
    driver = start_browser.sessions[session_id]
    
    results = {
        "query": query,
        "search_engine": search_engine,
        "pages_visited": 0,
        "results": [],
        "status": "success"
    }
    
    try:
        # Determine search engine URL
        if search_engine.lower() == "google":
            search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
        elif search_engine.lower() == "bing":
            search_url = f"https://www.bing.com/search?q={urllib.parse.quote_plus(query)}"
        elif search_engine.lower() == "ddg" or search_engine.lower() == "duckduckgo":
            search_url = f"https://duckduckgo.com/?q={urllib.parse.quote_plus(query)}"
        else:
            # Default to Google
            search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
            results["search_engine"] = "google"
        
        # Navigate to search engine
        driver.get(search_url)
        time.sleep(3)  # Wait for page to load
        
        # Get search result links based on the search engine
        search_results = []
        if search_engine.lower() == "google":
            # Find all search result elements
            result_elements = driver.find_elements(By.CSS_SELECTOR, "div.g div.yuRUbf > a, div.g h3.LC20lb")
            
            for element in result_elements:
                try:
                    # Try to get the parent anchor element if we found the title
                    if element.tag_name == "h3":
                        # Find the parent anchor
                        parent = element.find_element(By.XPATH, "./..")
                        while parent.tag_name != "a" and parent.tag_name != "body":
                            parent = parent.find_element(By.XPATH, "./..")
                        
                        if parent.tag_name == "a":
                            url = parent.get_attribute("href")
                            title = element.text
                            search_results.append({"url": url, "title": title})
                    else:
                        # We found the anchor directly
                        url = element.get_attribute("href")
                        title_element = element.find_element(By.CSS_SELECTOR, "h3")
                        title = title_element.text if title_element else "No title"
                        search_results.append({"url": url, "title": title})
                except Exception as e:
                    # Skip problematic elements
                    continue
        
        elif search_engine.lower() == "bing":
            result_elements = driver.find_elements(By.CSS_SELECTOR, "li.b_algo h2 a")
            for element in result_elements:
                url = element.get_attribute("href")
                title = element.text
                search_results.append({"url": url, "title": title})
        
        elif search_engine.lower() in ["ddg", "duckduckgo"]:
            result_elements = driver.find_elements(By.CSS_SELECTOR, ".result__a")
            for element in result_elements:
                url = element.get_attribute("href")
                title = element.text
                search_results.append({"url": url, "title": title})
        
        # Limit to max_pages
        search_results = search_results[:max_pages]
        results["total_search_results"] = len(search_results)
        
        # Helper function to extract text content relevant to the query
        def extract_relevant_text(html_content, query_terms):
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text content
            text = soup.get_text(separator=" ", strip=True)
            
            # Split query into terms
            if isinstance(query_terms, str):
                query_terms = query_terms.lower().split()
            
            # Find paragraphs that contain query terms
            paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n|\r\s*\r', text)
            relevant_paragraphs = []
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if len(paragraph) < 20:  # Skip very short paragraphs
                    continue
                
                paragraph_lower = paragraph.lower()
                relevance_score = sum(1 for term in query_terms if term.lower() in paragraph_lower)
                
                if relevance_score > 0:
                    relevant_paragraphs.append({
                        "text": paragraph,
                        "relevance_score": relevance_score
                    })
            
            # Sort by relevance score
            relevant_paragraphs.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Return top paragraphs (up to 3)
            return relevant_paragraphs[:3]
        
        # Track visited URLs to avoid duplicates
        visited_urls = set()
        query_terms = query.split()
        
        # Process each search result
        for idx, result in enumerate(search_results):
            try:
                url = result["url"]
                title = result["title"]
                
                # Skip if already visited
                if url in visited_urls:
                    continue
                
                # Visit the page
                driver.get(url)
                visited_urls.add(url)
                time.sleep(3)  # Wait for page to load
                results["pages_visited"] += 1
                
                # Get the page content
                page_html = driver.page_source
                page_title = driver.title
                
                # Extract relevant content
                page_result = {
                    "url": url,
                    "title": page_title or title,
                    "relevant_content": []
                }
                
                if extract_relevant_content:
                    relevant_paragraphs = extract_relevant_text(page_html, query_terms)
                    page_result["relevant_content"] = relevant_paragraphs
                
                # Add to results
                results["results"].append(page_result)
                
                # If depth > 1, follow links that might be relevant
                if depth > 1 and results["pages_visited"] < max_pages:
                    # Find links that might be relevant
                    soup = BeautifulSoup(page_html, "html.parser")
                    links = soup.find_all("a", href=True)
                    potential_links = []
                    
                    for link in links:
                        link_text = link.text.strip().lower()
                        link_url = link["href"]
                        
                        # Check if link text contains any query terms
                        is_relevant = any(term.lower() in link_text for term in query_terms)
                        
                        # Ensure it's a proper URL (not javascript:, mailto:, etc)
                        is_proper_url = link_url.startswith("http") or link_url.startswith("/")
                        
                        if is_relevant and is_proper_url:
                            # Convert relative URLs to absolute
                            if link_url.startswith("/"):
                                # Get the base URL
                                base_url = '/'.join(url.split('/')[:3])  # http(s)://domain.com
                                link_url = base_url + link_url
                            
                            potential_links.append({
                                "url": link_url,
                                "text": link_text
                            })
                    
                    # Visit up to 2 relevant internal links
                    for link_idx, link in enumerate(potential_links[:2]):
                        if results["pages_visited"] >= max_pages:
                            break
                        
                        if link["url"] not in visited_urls:
                            try:
                                driver.get(link["url"])
                                visited_urls.add(link["url"])
                                time.sleep(3)  # Wait for page to load
                                results["pages_visited"] += 1
                                
                                sub_page_html = driver.page_source
                                sub_page_title = driver.title
                                
                                # Extract relevant content
                                sub_page_result = {
                                    "url": link["url"],
                                    "title": sub_page_title,
                                    "source": f"Link from {url}",
                                    "link_text": link["text"],
                                    "relevant_content": []
                                }
                                
                                if extract_relevant_content:
                                    relevant_paragraphs = extract_relevant_text(sub_page_html, query_terms)
                                    sub_page_result["relevant_content"] = relevant_paragraphs
                                
                                # Add to results
                                results["results"].append(sub_page_result)
                            except Exception as e:
                                # Skip problematic pages
                                continue
            
            except Exception as e:
                # Skip problematic search results
                continue
        
        # Process the collected information to create a summary
        if extract_relevant_content and results["results"]:
            all_relevant_content = []
            for page in results["results"]:
                for content in page["relevant_content"]:
                    all_relevant_content.append({
                        "text": content["text"],
                        "relevance_score": content["relevance_score"],
                        "source": page["url"],
                        "title": page["title"]
                    })
            
            # Sort by relevance score
            all_relevant_content.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Add summary to results
            results["top_relevant_content"] = all_relevant_content[:5]  # Top 5 most relevant paragraphs
        
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    finally:
        # Close the browser
        close_browser(session_id)
    
    return results

@mcp.tool()
def answer_question_from_web(question: str, max_pages: int = 8, search_depth: int = 2) -> dict:
    """Search the web for information to answer a specific question
    
    Parameters:
    - question: The question to find an answer for
    - max_pages: Maximum number of pages to explore (default: 8)
    - search_depth: How deep to navigate from search results (default: 2)
    """
    import re
    from collections import Counter
    
    # Clean up the question and extract keywords
    clean_question = re.sub(r'[?.,;:!]', '', question).lower()
    
    # Identify question type
    question_type = "unknown"
    if re.match(r'^(what|who|where|when|why|how|which|can|will|is|are|does|do|did|should|would|could|has|have)\b', clean_question):
        question_type = re.match(r'^(what|who|where|when|why|how|which|can|will|is|are|does|do|did|should|would|could|has|have)\b', clean_question).group(0)
    
    # Perform deep web search
    search_results = deep_web_search(
        query=question,
        max_pages=max_pages,
        search_engine="google",
        depth=search_depth,
        extract_relevant_content=True
    )
    
    # If search failed, return error
    if search_results["status"] != "success" or not search_results["results"]:
        return {
            "status": "error",
            "message": "Failed to find relevant information",
            "question": question,
            "question_type": question_type
        }
    
    # Analyze the search results to find the most relevant information
    answer_candidates = []
    
    # Process all the relevant content from the search results
    if "top_relevant_content" in search_results:
        for content in search_results["top_relevant_content"]:
            text = content["text"]
            relevance = content["relevance_score"]
            source = content["source"]
            title = content["title"]
            
            # Check if the text directly contains answer patterns based on question type
            answer_indicators = False
            
            if question_type == "what":
                answer_indicators = re.search(r'is\s+[^.?!]+', text, re.IGNORECASE) is not None
            elif question_type == "who":
                answer_indicators = re.search(r'(is|was)\s+[^.?!]+', text, re.IGNORECASE) is not None
            elif question_type == "where":
                answer_indicators = re.search(r'(in|at|on|located\s+in|near)\s+[^.?!]+', text, re.IGNORECASE) is not None
            elif question_type == "when":
                answer_indicators = re.search(r'(in|on|at|during)\s+[0-9]|january|february|march|april|may|june|july|august|september|october|november|december', text, re.IGNORECASE) is not None
            elif question_type == "why":
                answer_indicators = re.search(r'because|since|due\s+to|as\s+a\s+result\s+of', text, re.IGNORECASE) is not None
            elif question_type == "how":
                answer_indicators = re.search(r'by\s+[^.?!]+|through\s+[^.?!]+|using\s+[^.?!]+', text, re.IGNORECASE) is not None
            
            # Score the candidate based on factors
            score = relevance
            if answer_indicators:
                score += 3
            
            # Add question terms that appear in the text
            question_terms = clean_question.split()
            question_term_matches = sum(1 for term in question_terms if term.lower() in text.lower() and len(term) > 3)
            score += question_term_matches * 0.5
            
            # Look for numbers if the question likely requires a numeric answer
            if re.search(r'\b(how much|how many|how old|how long|how far|how high|how wide|how tall)\b', clean_question, re.IGNORECASE):
                if re.search(r'\b\d+\.?\d*\b', text):
                    score += 2
            
            answer_candidates.append({
                "text": text,
                "score": score,
                "source": source,
                "title": title
            })
    
    # Sort candidates by score
    answer_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Prepare answer
    answer = {
        "status": "success",
        "question": question,
        "question_type": question_type,
        "answer_sources": [],
        "confidence": 0
    }
    
    # Extract the top candidates
    top_candidates = answer_candidates[:3]
    
    if top_candidates:
        answer["answer_sources"] = [{
            "text": candidate["text"],
            "score": candidate["score"],
            "source": candidate["source"],
            "title": candidate["title"]
        } for candidate in top_candidates]
        
        # Calculate overall confidence based on scores
        if len(top_candidates) > 0:
            max_score = top_candidates[0]["score"]
            answer["confidence"] = min(1.0, max_score / 10)  # Scale confidence
    
    # Add search metadata
    answer["search_metadata"] = {
        "pages_visited": search_results["pages_visited"],
        "total_search_results": search_results.get("total_search_results", 0)
    }
    
    return answer

@mcp.tool()
def fetch_images_from_website(url: str, save_dir: str, selectors: list = None, max_images: int = 50) -> dict:
    """Fetch images from a website and save them to a directory
    
    Parameters:
    - url: The URL of the website to fetch images from
    - save_dir: The directory to save images to
    - selectors: CSS selectors to target specific images (default: None, gets all images)
    - max_images: Maximum number of images to fetch (default: 50)
    """
    import os
    import time
    import re
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse

    result = {
        "status": "success",
        "url": url,
        "saved_images": [],
        "failed_images": []
    }
    
    # Create directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Start a browser session to handle JavaScript-rendered content
    browser_session = start_browser(headless=True)
    session_id = browser_session["session_id"]
    
    try:
        # Navigate to URL
        driver = start_browser.sessions[session_id]
        driver.get(url)
        
        # Give the page some time to load
        time.sleep(5)
        
        # Get page source after JavaScript execution
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find images based on selectors or get all images
        if selectors:
            all_images = []
            for selector in selectors:
                selected_elements = soup.select(selector)
                for element in selected_elements:
                    if element.name == 'img':
                        all_images.append(element)
                    else:
                        # If the element is not an img tag, find all img tags inside it
                        all_images.extend(element.find_all('img'))
        else:
            # Get all images
            all_images = soup.find_all('img')
        
        # Limit the number of images
        all_images = all_images[:max_images]
        
        # Keep track of duplicate filenames
        filename_counts = {}
        
        # Process each image
        for i, img in enumerate(all_images):
            # Get image source
            src = img.get('src')
            
            # Skip if no source
            if not src:
                result["failed_images"].append({
                    "reason": "No source attribute",
                    "element": str(img)
                })
                continue
            
            # Handle data URIs (base64 encoded images)
            if src.startswith('data:image'):
                try:
                    import base64
                    # Extract the image format and base64 data
                    format_match = re.search(r'data:image/(\w+);base64,', src)
                    if format_match:
                        image_format = format_match.group(1)
                        base64_data = src.split(',')[1]
                        
                        # Generate filename
                        filename = f"data_image_{i}.{image_format}"
                        filepath = os.path.join(save_dir, filename)
                        
                        # Save image
                        with open(filepath, 'wb') as f:
                            f.write(base64.b64decode(base64_data))
                        
                        result["saved_images"].append({
                            "original_url": "data:image",
                            "saved_path": filepath,
                            "type": "base64"
                        })
                    else:
                        result["failed_images"].append({
                            "original_url": src[:50] + "...",
                            "reason": "Invalid data URI format"
                        })
                except Exception as e:
                    result["failed_images"].append({
                        "original_url": src[:50] + "...",
                        "reason": f"Error processing data URI: {str(e)}"
                    })
                continue
            
            # Process regular URLs
            try:
                # Make absolute URL if needed
                if not urlparse(src).netloc:
                    src = urljoin(url, src)
                
                # Get image content
                img_response = requests.get(src, stream=True, timeout=10)
                if img_response.status_code != 200:
                    result["failed_images"].append({
                        "original_url": src,
                        "reason": f"HTTP status code: {img_response.status_code}"
                    })
                    continue
                
                # Determine image type from Content-Type or URL
                content_type = img_response.headers.get('Content-Type', '')
                if 'image' in content_type:
                    ext = content_type.split('/')[-1].lower()
                    if ext == 'jpeg':
                        ext = 'jpg'
                else:
                    # Try to get extension from URL
                    path = urlparse(src).path
                    ext = os.path.splitext(path)[1].lower()
                    if not ext or ext == '.':
                        ext = '.jpg'  # Default to jpg
                    else:
                        ext = ext[1:]  # Remove the dot
                
                # Clean up filename from URL path
                url_filename = os.path.basename(urlparse(src).path)
                url_filename = re.sub(r'[^\w\-\.]', '_', url_filename)
                
                # If filename is empty or invalid, generate one
                if not url_filename or url_filename == '.':
                    # Get alt text or title attribute if available
                    alt_text = img.get('alt', '')
                    title_text = img.get('title', '')
                    
                    if alt_text:
                        # Clean up alt text to use as filename
                        filename_base = re.sub(r'[^\w\-]', '_', alt_text)[:30]  # Limit length
                    elif title_text:
                        # Clean up title text to use as filename
                        filename_base = re.sub(r'[^\w\-]', '_', title_text)[:30]  # Limit length
                    else:
                        # Generate filename based on domain and index
                        domain = urlparse(url).netloc.split('.')[0]
                        filename_base = f"{domain}_image_{i}"
                
                    filename = f"{filename_base}.{ext}"
                else:
                    # Check if the URL filename has an extension
                    if '.' in url_filename:
                        filename = url_filename
                    else:
                        filename = f"{url_filename}.{ext}"
                
                # Handle duplicate filenames
                if filename in filename_counts:
                    filename_counts[filename] += 1
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{filename_counts[filename]}{ext}"
                else:
                    filename_counts[filename] = 1
                
                # Save image
                filepath = os.path.join(save_dir, filename)
                with open(filepath, 'wb') as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Record success
                result["saved_images"].append({
                    "original_url": src,
                    "saved_path": filepath,
                    "type": "remote"
                })
            
            except Exception as e:
                result["failed_images"].append({
                    "original_url": src,
                    "reason": str(e)
                })
        
        # Add summary information
        result["total_found"] = len(all_images)
        result["total_saved"] = len(result["saved_images"])
        result["total_failed"] = len(result["failed_images"])
        
    except Exception as e:
        result["status"] = "error"
        result["error_message"] = str(e)
    
    finally:
        # Close the browser
        close_browser(session_id)
    
    return result

@mcp.tool()
def fetch_naver_assets(save_dir: str = "naver_clone/images") -> dict:
    """Fetch essential assets from Naver website for the clone project
    
    This function specifically targets Naver's key visual elements:
    - Logo
    - Icons
    - News media logos
    - Banner images
    
    Parameters:
    - save_dir: Directory to save the images to (default: "naver_clone/images")
    """
    import os
    import time
    
    result = {
        "status": "success",
        "saved_assets": {
            "logo": [],
            "icons": [],
            "media_logos": [],
            "banners": []
        }
    }
    
    # Make sure the directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Start browser session
    browser_session = start_browser(headless=True)
    session_id = browser_session["session_id"]
    
    try:
        # Navigate to Naver homepage
        driver = start_browser.sessions[session_id]
        driver.get("https://www.naver.com/")
        
        # Wait for page to load completely
        time.sleep(5)
        
        # Take screenshot for reference
        screenshot_path = os.path.join(save_dir, "naver_reference.png")
        driver.save_screenshot(screenshot_path)
        result["reference_screenshot"] = screenshot_path
        
        # Fetch logo
        logo_result = fetch_images_from_website(
            url="https://www.naver.com/",
            save_dir=os.path.join(save_dir, "logo"),
            selectors=[".logo_naver", ".search_logo a", "#special-input-logo", "h1.search_logo a"],
            max_images=5
        )
        result["saved_assets"]["logo"] = logo_result.get("saved_images", [])
        
        # Fetch icons and sprites
        # Use JavaScript execution to identify sprite images
        sprite_urls = driver.execute_script("""
            const spriteUrls = new Set();
            const styleSheets = Array.from(document.styleSheets);
            
            try {
                styleSheets.forEach(sheet => {
                    try {
                        if (sheet.cssRules) {
                            Array.from(sheet.cssRules).forEach(rule => {
                                if (rule.style && rule.style.backgroundImage) {
                                    const urlMatch = rule.style.backgroundImage.match(/url\\(['"]?([^'")]+)['"]?\\)/);
                                    if (urlMatch && urlMatch[1]) {
                                        spriteUrls.add(urlMatch[1]);
                                    }
                                }
                            });
                        }
                    } catch (e) {
                        // Ignore security errors for cross-origin stylesheets
                    }
                });
            } catch (e) {
                // Fallback if accessing styleSheets fails
            }
            
            return Array.from(spriteUrls);
        """)
        
        # Save sprite URLs
        result["sprite_urls"] = sprite_urls
        
        # Process each sprite URL
        import requests
        from urllib.parse import urljoin
        
        for i, sprite_url in enumerate(sprite_urls):
            try:
                # Make absolute URL if needed
                if not sprite_url.startswith('http'):
                    sprite_url = urljoin("https://www.naver.com/", sprite_url)
                
                # Download sprite image
                sprite_response = requests.get(sprite_url, timeout=10)
                if sprite_response.status_code == 200:
                    # Determine filename
                    if 'sp_main' in sprite_url or 'main' in sprite_url:
                        filename = "sp_main.png"
                    elif 'sprite' in sprite_url:
                        filename = "sprite_icons.png"
                    else:
                        filename = f"sprite_{i}.png"
                    
                    # Save sprite
                    sprite_path = os.path.join(save_dir, filename)
                    with open(sprite_path, 'wb') as f:
                        f.write(sprite_response.content)
                    
                    result["saved_assets"]["icons"].append({
                        "original_url": sprite_url,
                        "saved_path": sprite_path
                    })
            except Exception as e:
                result["errors"] = result.get("errors", []) + [{
                    "message": f"Error saving sprite {sprite_url}: {str(e)}"
                }]
        
        # Fetch media logos (news sources)
        media_result = fetch_images_from_website(
            url="https://www.naver.com/",
            save_dir=os.path.join(save_dir, "media"),
            selectors=[".media_grid img", ".media_item img", ".news_logo img", "[class*='subscription'] img"],
            max_images=30
        )
        
        # Rename media logos sequentially for our template
        import shutil
        for i, img in enumerate(media_result.get("saved_images", [])):
            original_path = img["saved_path"]
            if os.path.exists(original_path):
                extension = os.path.splitext(original_path)[1]
                new_filename = f"media{i+1}{extension}"
                new_path = os.path.join(save_dir, new_filename)
                shutil.copy2(original_path, new_path)
                img["template_path"] = new_path
        
        result["saved_assets"]["media_logos"] = media_result.get("saved_images", [])
        
        # Fetch banner images
        banner_result = fetch_images_from_website(
            url="https://www.naver.com/",
            save_dir=os.path.join(save_dir, "banner"),
            selectors=[".banner_box img", ".banner_rolling img", ".ad_area img", "[class*='banner'] img"],
            max_images=10
        )
        
        # Rename banner images sequentially for our template
        for i, img in enumerate(banner_result.get("saved_images", [])):
            original_path = img["saved_path"]
            if os.path.exists(original_path):
                extension = os.path.splitext(original_path)[1]
                new_filename = f"banner{i+1}{extension}"
                new_path = os.path.join(save_dir, new_filename)
                shutil.copy2(original_path, new_path)
                img["template_path"] = new_path
        
        result["saved_assets"]["banners"] = banner_result.get("saved_images", [])
        
        # Fetch favicon
        try:
            import requests
            favicon_url = "https://www.naver.com/favicon.ico"
            favicon_response = requests.get(favicon_url, timeout=10)
            if favicon_response.status_code == 200:
                favicon_path = os.path.join(save_dir, "favicon.ico")
                with open(favicon_path, 'wb') as f:
                    f.write(favicon_response.content)
                result["saved_assets"]["favicon"] = favicon_path
        except Exception as e:
            result["errors"] = result.get("errors", []) + [{
                "message": f"Error saving favicon: {str(e)}"
            }]
        
        # Summarize results
        result["total_saved"] = (
            len(result["saved_assets"]["logo"]) + 
            len(result["saved_assets"]["icons"]) + 
            len(result["saved_assets"]["media_logos"]) + 
            len(result["saved_assets"]["banners"]) + 
            (1 if "favicon" in result["saved_assets"] else 0)
        )
        
    except Exception as e:
        result["status"] = "error"
        result["error_message"] = str(e)
    
    finally:
        # Close browser
        close_browser(session_id)
    
    return result

if __name__ == "__main__":
    # Run the server
    mcp.run() 