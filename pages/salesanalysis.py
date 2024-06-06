import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Output, Input

dash.register_page(__name__, path = "/sales")

superstore = pd.read_csv("data/Sample - Superstore.csv", encoding = "latin1")

superstore['Order Date'] = pd.to_datetime(superstore['Order Date'], format = "%m/%d/%Y")

# Country Distribution of products sold to

countryquantity = superstore.groupby('Country')['Quantity'].sum().reset_index()

countryquantitydistribution = px.scatter_geo(countryquantity, locations = countryquantity['Country'], locationmode = "country names", projection = "natural earth",
                                            size = countryquantity.groupby("Country")['Quantity'].sum().values, color = countryquantity.groupby("Country")['Quantity'].sum().values, color_continuous_scale = "magma_r")

countryquantitydistribution.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)", title = dict(font = dict(color = "white", size = 14)), geo = dict(bgcolor = "rgba(0, 0, 0, 0)", landcolor = "slategrey", showcountries = True))

countryquantitydistribution.update_geos(showframe = True)

countryquantitydistribution.update_coloraxes(colorbar_tickfont_color = "white", colorbar_title = "Quantity Sold", colorbar_title_font_color = "White")


# Monthly trend of quantity sold

monthlycategorytrend = superstore.groupby(['Category', pd.Grouper(key = "Order Date", freq = "M")])['Quantity'].sum().reset_index()

monthlycategorytrenddistribution = px.line(monthlycategorytrend, x = "Order Date", y = "Quantity", color = "Category", title = "Monthly Trend for Categories Sold", line_shape = "spline")

monthlycategorytrenddistribution.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)", plot_bgcolor = "rgba(0, 0, 0, 0)", title_font_color = "white", legend_font_color = "white",
                                            xaxis_tickfont_color = 'White', yaxis_tickfont_color = "white", xaxis_title = "", yaxis_title = "", yaxis_showticklabels = False)

monthlycategorytrenddistribution.update_yaxes(showgrid = False, zeroline = False)

monthlycategorytrenddistribution.update_xaxes(showgrid = False)

datasize = superstore.shape[0]

card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.P(
                    datasize,
                    className="text-light",
                ),
                html.H4("Data Size", className="text-warning"),
            ]
        ),
    ],
    class_name = "bg-transparent border-warning w-auto d-flex justify-content-center",
)

layout = dbc.Container(
    [
        dbc.Row(
            card
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        superstore['Segment'].unique(),
                        className = "mt-5",
                        id = "segment-dropdown",
                        placeholder = "Select a Segment",
                        optionHeight = 50,
                        style = {
                        "background-color": "rgba(0,0,0,0)",
                        "color" : 'black',
                        "border-color" : 'yellow',
                        "border-radius" : '25px'
                        }
                    )
                ),
                dbc.Col(
                    dcc.RangeSlider(
                        superstore['Order Date'].dt.year.min(),
                        superstore['Order Date'].dt.year.max(),
                        1,
                        id = "year-range",
                        className = "mt-5"
                    )
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id ="category-quantity-distribution", responsive = True)),
                dbc.Col(dcc.Graph(id = "category-subcategory-quantity-distribution", responsive = True)),
                dbc.Col(dcc.Graph(id = "city-quantity-distribution", responsive = True)),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure = countryquantitydistribution)),
                dbc.Col(dcc.Graph(id = "city-subcategory-distribution")),
            ]
        ),
        dbc.Row(
            [
                dcc.Graph(figure = monthlycategorytrenddistribution)
            ]
        )
    ],
    fluid = True
)

@callback(
    Output('category-quantity-distribution', 'figure'),
    Output('category-subcategory-quantity-distribution', 'figure'),
    Output('city-quantity-distribution', 'figure'),
    Input('segment-dropdown', 'value'),
    Input('year-range', 'value'),
)
def categoryquantitydistributionfilter(segment, year):
    if segment and year:
        superstore_segment_filter = superstore[
            (superstore['Segment'] == segment) &
            (superstore['Order Date'].dt.year >= year[0]) &
            (superstore['Order Date'].dt.year <= year[-1])
        ]
    
    elif segment:
        superstore_segment_filter = superstore[superstore['Segment'] == segment]

    elif year:
        superstore_segment_filter = superstore[
                    (superstore['Order Date'].dt.year >= year[0]) &
                    (superstore['Order Date'].dt.year <= year[-1])
                ]
   
    else:
        superstore_segment_filter = superstore

    categoryquantity = superstore_segment_filter.groupby('Category')['Quantity'].sum()    # Creating a plotly express doughnut chart 

    # Creating a new dataframe that has a grouped Category and Sub-Category
    category_subcategory_quantity = superstore_segment_filter.groupby(['Category', 'Sub-Category'])['Quantity'].sum().reset_index()

    # Find the total quantity sold in the entire dataset
    quantitysold = superstore_segment_filter.Quantity.sum()

    # Finding the top 3 cities based on quantity sold
    top3cities = superstore_segment_filter.groupby('City')['Quantity'].sum().nlargest(3)
    

    # Category Distribution Chart

    categoryquantitydistribution = px.pie(names = categoryquantity.index, values = categoryquantity.values, hole = 0.7, color_discrete_sequence=px.colors.qualitative.Dark24_r)

    # Changing the graph, title and legend colors to white
    categoryquantitydistribution.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)", legend_font_color = "white")

    # Finding total quantity sold based on category
    totalquantitysold = '{:,}'.format(categoryquantity.sum()) # Adding the comma where necessary for cases of thousands, hundreds of thousands, millions, billions, trillions etc.

    # Adding the text in the middle of the doughnut chart 
    categoryquantitydistribution.add_annotation(text = "Total Sold", showarrow = False, font_color = "white", y = 0.55, font_size = 14) # Adding the title
    categoryquantitydistribution.add_annotation(text = totalquantitysold, showarrow = False, font_color = "white", y = 0.45, font_size = 14) # Adding the total quantity sold calculated

    # Category Sub-Category Distribution Chart

    # Create a sunburst showing the distribution of category and sub-category on a parent-child relationship
    category_subcategory_quantity_distribution = px.sunburst(category_subcategory_quantity, path = ['Category', 'Sub-Category'], values = "Quantity")

    # Changing the graph, title and legend colors to white
    category_subcategory_quantity_distribution.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)", legend_font_color = "white")

    # Give the different sub-categories different colors
    category_subcategory_quantity_distribution.update_traces(marker_colors = px.colors.qualitative.Dark24_r)

    # Top 3 cities sold to based on quantity

    # Find the total quantity sold based on the top 3 cities
    top3citiesgrouped = top3cities.sum()

    # Finding percentage distribution of total quantity sold in top 3 cities to total quantity sold in the entire dataset
    percentagedistribution = (top3cities / quantitysold) * 100

    distributionlabels = [f"{city} : {percentage : .2f}%" for city, percentage in zip(top3cities.index, percentagedistribution)]

    # Creating the doughnut chart showing the distriubtion based on the top 3 cities
    cityquantitydistribution = px.pie(names = distributionlabels, values = top3cities.values, hole = 0.7, color_discrete_sequence=px.colors.qualitative.Dark24_r)

    # Changing the graph, title and legend colors to white
    cityquantitydistribution.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)", legend_font_color = "white")

    # Adding the text in the middle of the doughnut chart
    cityquantitydistribution.add_annotation(text = "Top 3 Cities", showarrow = False, font = dict(color = "white"), y = 0.6)
    cityquantitydistribution.add_annotation(text = "Total Sold", showarrow = False, font = dict(color = "white"))
    cityquantitydistribution.add_annotation(text = '{:,}'.format(top3citiesgrouped), showarrow = False, font = dict(size = 14, color = "white"), y = 0.4)

    return categoryquantitydistribution, category_subcategory_quantity_distribution, cityquantitydistribution

@callback(
    Output('city-subcategory-distribution', 'figure'),
    Input('category-quantity-distribution', 'clickData'),
)
def cross_filtering(clickData):
    # Sub-Category Distribution by top 3 cities

    if clickData:
        superstore_category_subcategory_filter = superstore[superstore['Category'] == clickData['points'][0]['label']]
        city_subcategory_quantity = superstore_category_subcategory_filter.groupby(['City', 'Sub-Category'])['Quantity'].sum().reset_index()

    else:
        city_subcategory_quantity = superstore.groupby(['City', 'Sub-Category'])['Quantity'].sum().reset_index()


    city_subcategory_quantity_top_3 = city_subcategory_quantity.groupby('City')['Quantity'].sum().nlargest(3).index

    city_subcategory_quantity_filtered = city_subcategory_quantity[city_subcategory_quantity['City'].isin(city_subcategory_quantity_top_3)]

    city_subcategory_distribution = px.bar(city_subcategory_quantity_filtered, x = "City", y = "Quantity",
                                            color = "Sub-Category", barmode='group', text = "Quantity", color_discrete_sequence = px.colors.qualitative.Dark24_r)

    city_subcategory_distribution.update_layout(paper_bgcolor = "rgba(0, 0, 0, 0)", plot_bgcolor = "rgba(0, 0, 0, 0)", legend_font_color = "white",
                                                xaxis_tickfont_color = 'White', yaxis_tickfont_color = "white", xaxis_title = "", yaxis_title = "", yaxis_showticklabels = False, bargap = 0.1)

    city_subcategory_distribution.update_yaxes(showgrid = False, zeroline = False)

    city_subcategory_distribution.update_traces(marker_line_width = 0, textposition = "outside", textfont_color = 'white', textfont_size = 10)

    return city_subcategory_distribution