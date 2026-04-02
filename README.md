# 2gis-scraper

A Python-based scraper for collecting place data from 2GIS using SeleniumBase, explicit waits, custom progress bars, and structured export to Excel.

## Overview

This project is a practical parser for extracting data from 2GIS search results pages.  
It was built as an engineering-focused scraping workflow rather than a one-off script, with attention to browser configuration, loading strategy, structured data extraction, and readable runtime monitoring.

The scraper is designed to work with dynamic 2GIS pages and collect information such as:

- Company name
- Category
- Rating
- Number of reviews
- Address
- Additional card attributes
- URL
- Coordinates extracted from route links

The project uses **SeleniumBase** as the browser automation layer and applies a set of configuration choices aimed at making scraping both faster and more stable in dynamic SPA-like environments.

## Why this project is interesting

2GIS is not a simple static website. Search results and place cards are rendered dynamically, which means classic HTML-only parsing approaches are often insufficient.  
Because of that, the project uses a browser-driven approach with SeleniumBase and explicit waiting logic for reliable interaction with the page.

A key implementation detail is the use of a tuned browser loading strategy.  
The driver is configured with `page_load_strategy="eager"`, which allows the scraper to continue as soon as the DOM is ready instead of waiting for the full page, map rendering, and all visual assets to finish loading.  
In practice, this makes a big difference: for parsing search listings, full map rendering is unnecessary, so skipping heavy visual loading helps reduce wasted time and improves overall throughput.

Another distinctive part of the project is the custom progress bar implementation.  
Instead of using a default `tqdm` bar, the parser includes a small custom wrapper with sensible defaults, nested progress support, and a helper method for updating runtime status fields.  
This makes long scraping sessions much easier to monitor and gives the project a cleaner, more polished feel.

## Features

- Dynamic scraping of 2GIS search results
- SeleniumBase-based browser automation
- Optimized page loading via `page_load_strategy="eager"`
- Support for stealth-oriented driver setup
- Custom progress bar built on top of `tqdm`
- Nested progress bars for page-level and item-level tracking
- Coordinate extraction from 2GIS route URLs
- Structured collection of card attributes
- Excel export through `pandas`
- Clear separation between notebook workflow and reusable utility functions

## Tech stack

- Python
- SeleniumBase
- Selenium / WebDriver
- pandas
- tqdm
- openpyxl
- Jupyter Notebook

## Core ideas behind the implementation

### 1. SeleniumBase instead of plain Selenium

The project relies on **SeleniumBase** rather than raw Selenium setup.  
This makes the code more ergonomic and provides access to additional browser control helpers, cleaner waiting methods, and a more practical setup for modern websites.

For scraping dynamic services like 2GIS, this improves both readability and developer experience.  
The goal here was not only to make the parser work, but also to make the workflow easier to maintain, extend, and demonstrate publicly.

### 2. Faster scraping through eager loading

One of the most important implementation choices is the browser loading strategy:

```python
page_load_strategy="eager"
```

This means the browser does not wait for every heavy asset to finish loading.  
For this project, that is exactly the desired behavior, because the task is to parse search result cards rather than interact with the fully rendered map interface.

In other words:

- The map does not need to fully load
- Visual completeness is not the goal
- DOM availability is enough
- Faster continuation means faster scraping

This is a good example of adapting the browser configuration to the actual data extraction task.

### 3. Explicit waits for dynamic content

Instead of relying on fragile timing with hardcoded delays only, the parser uses explicit waits where possible.  
That approach is more robust for dynamic pages and helps avoid unnecessary waiting when elements become available earlier.

This is especially important for:

- Search result cards
- Place details
- Route link availability
- Pagination transitions

The scraper waits for the required DOM state and then proceeds with extraction.

### 4. Custom progress bar

A separate part of the project is a custom progress bar implementation built on top of `tqdm`.

It includes:

- Custom defaults for parsing workflows
- Better visual presentation
- Support for nested progress bars
- Helper method for updating status fields
- Cleaner tracking of page loops and item loops

This allows the scraper to show progress on two levels:

1. Pagination progress
2. Processing progress for individual places on each page

That may seem like a small detail, but in real long-running parsers, good runtime visibility makes a big difference.  
It improves debugging, monitoring, and the overall quality of the workflow.

## Data extraction logic

The parser follows a simple but practical workflow:

1. Start a configured SeleniumBase driver
2. Open the target 2GIS page
3. Detect total number of places
4. Estimate total pagination length
5. Iterate through pages
6. Collect all visible result cards on the page
7. Open each place card
8. Extract route link and parse coordinates
9. Extract visible card attributes
10. Append the result to a pandas DataFrame
11. Save results to Excel

The extracted fields include both structured values and some raw card content, which is useful for later cleaning, debugging, or schema refinement.

## Example use case

This parser can be used as a starting point for tasks such as:

- Building local business datasets
- Collecting organization listings by city
- Extracting addresses and coordinates for GIS workflows
- Preparing source tables for data cleaning and geospatial enrichment
- Testing browser-based scraping strategies for modern map services

## Notes

- The project is intended for educational, research, and portfolio purposes.
- Website structure may change over time, so selectors may require updates.
- Browser-driven parsers are more sensitive to UI changes than API-based workflows.
- Depending on the environment, local browser setup may affect behavior.

## What this repository demonstrates

This repository is meant to showcase more than just scraping itself.  
It demonstrates:

- Practical work with dynamic web pages
- Thoughtful browser configuration
- Reusable utility design
- Runtime monitoring through custom progress bars
- Structured extraction workflow
- Clean separation between experimentation and reusable code

From a portfolio perspective, the goal of this repository is to present the project not as a “quick notebook hack”, but as a compact and well-organized scraping tool with clear engineering decisions behind it.

## Future improvements

Possible next steps for the project:

- Move from notebook-first usage to a CLI script
- Add configuration through `.env` or YAML
- Save data in CSV / Parquet in addition to Excel
- Introduce logging instead of plain prints
- Add retry logic for unstable UI states
- Refactor selectors into a dedicated config block
- Add screenshots or GIF previews to the README
- Add sample output file
- Add automatic deduplication
- Add export for geospatial workflows

## Disclaimer

Use this project responsibly and in accordance with the target website’s terms of use, robots rules, and applicable laws.  
The repository is presented as a technical demonstration of browser automation and structured data extraction techniques.

---
