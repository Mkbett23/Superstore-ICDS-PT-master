# Import the packages
from dash import Dash, html, dcc
import dash
# Making use of the bootstrap css framework
import dash_bootstrap_components as dbc

# Creating / Initializing the dash application
app = Dash(__name__,  external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

sidebar = dbc.Col(
    children = [
        html.Div(
            dcc.Link(
                f"{page['name']}",
                page["relative_path"],
                className="link-info link-underline-opacity-0"
            )
        ) for page in dash.page_registry.values()
    ],
    className="bg-success",
    width={"size" : 2}
)

charts = dbc.Col(
    dash.page_container
)

# Create the app components that will be displayed in my web browser
# One has to define the .layout so as to have the components of your website rendered to the browser
app.layout = dbc.Container(
    children = [
        dbc.Row(
            [
                sidebar,
                charts
            ]
        )
    ],
    className="bg-black",
    fluid = True
)

# Run the app
if __name__ == '__main__':
    app.run(debug = True, use_reloader = True)