### Project Overview

The aim of this project was to build an interactive dashboard to explore data regarding UK National Rail. The dashboard is split into 3 pages and can be navigated through the buttons at the top of each page.
The first page starts with some basic KPIs and then presents a few vizzes regarding most popular routes and revenue analysis. All charts are interactive, dropdown menus have a few options to choose from. 
The first graph is made with dash-cytoscape component, which is just perfect for network visualizations like rail routes. 
The graph is also interactive. When you hover over the nodes and edges of the graph, the information with station names and routes respectively is displayed. I also included data regarding tickets sold on the particular route.

![image](https://github.com/RadoslawStanisz/multipage_dashboard/assets/136122006/52267e02-5fea-4ab9-8ecc-5ad946d54f8d)

The other two charts present the revenue-related data. The first one allows users to choose time interval, and the second one enables them to analyze the revenue either by ticket type or ticket class. 
The last element of the first page is a table, which is also interactive. Users can choose the time interval from dropdown options, filter data and export data to xlsx. The other pages of the dashboard include several charts focusing on peak travel times, delays and customer behavior analysis. 

![image](https://github.com/RadoslawStanisz/multipage_dashboard/assets/136122006/923c1265-4f17-45ae-a7a6-1a5de72ad0fa)

### Dataset

The dataset is titled "UK Train Rides" and comes from [here](https://mavenanalytics.io/data-playground).
The data used in this dashboard ranges from the beginning of January 2024 till end of April 2024 and contains information on ticket purchase transactions along with many transaction details. 

### Analysis

The dashboard helps users to answer following questions:

- What are the most popular routes?
- What are the peak travel times?
- How does revenue vary by ticket types and classes?
- What is the on-time performance? What are the main contributing factors?

##### Assumptions

- All charts and tables related to revenue (including the figures in KPI section) use the data that was filtered in a way that they do NOT include transactions made before 01.01.2024 (There are a few transactions in the dataset with date of purchase before 2024). All other charts and figures (not related to revenue) use the full dataset. 
- The chart titled Revenue variability on a weekly timeframe has data till 28.04.2024. This is because on this day the full week ends.
- The difference between Total Revenue and Net Revenue is defined as follows: Net Revenue is a Total Revenue minus the amount corresponding to requested refunds (e.g., due to delays, cancellations, etc.).
- The ranking of most popular routes was made based on the number of tickets sold for particular route during the analysed period.

### Project output

The dashboard is an interactive web app built in Dash and Plotly. It can be run locally or can be viewed [here](https://multipage-dashboard-2.onrender.com/). **Since the app was deployed for demonstration purposes within a free tier on Render, it may take up to 1 minute to load.**


