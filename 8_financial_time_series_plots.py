import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.figure_factory as ff
import pandas_datareader as web
from dateutil.relativedelta import relativedelta
import datetime


app = dash.Dash()

stock_choices = [('Apple', 'AAPL'), ('IBM', 'IBM'),
                 ('Tesla', 'TSLA'), ('Amazon', 'AMZN')]

today_time = datetime.datetime.now()
today = datetime.date(today_time.year, today_time.month, today_time.day)

# The next variable is a year minus a day in the past
# This is because the Robinhood API from pandas_datareader can only go this far
first_date = today - relativedelta(years=1) + relativedelta(days=1)

app.layout = html.Div(
    [
        # The left most dropdown - this is to get the stock of interest
        html.Div(
            [
                html.H1('Pick Stock'),
                dcc.Dropdown(
                    id='stock',
                    options=[
                        {'label': i[0], 'value': i[1]} for i in stock_choices
                    ],
                    value='AAPL'
                )
            ], style={'width': '45%', 'display': 'inline-block',
                      'horizontal-align': 'center', 'vertical-align': 'top'}
        ),
        # The right widget - used to select the date
        html.Div(
            [
                html.H1('Pick Date Range'),
                dcc.DatePickerRange(
                    id='date_range',
                    min_date_allowed=first_date,
                    max_date_allowed=today,
                    initial_visible_month=today - relativedelta(months=6),
                    start_date=today - relativedelta(months=6),
                    end_date=today
                )
            ], style={'width': '45%', 'display': 'inline-block',
                      'textAlign': 'center'}
        ),
        html.P(
            html.Button(
                id='input_button',
                n_clicks=0,
                children='Submit',
                style=dict(fontSize=18)
            )
        ),
        dcc.Graph(
            id='candlestick'
        )
    ]
)


@app.callback(Output('candlestick', 'figure'),
              [Input('input_button', 'n_clicks')],
              [State('stock', 'value'),
               State('date_range', 'start_date'),
               State('date_range', 'end_date')])
def update_graph(n_clicks, stock, start, end):
    stock_df_all = web.DataReader(stock, 'robinhood').reset_index()
    stock_df = stock_df_all.loc[
        (stock_df_all['begins_at'] >= start) &
        (stock_df_all['begins_at'] <= end)
    ].reset_index()
    fig = ff.create_candlestick(
        open=stock_df['open_price'],
        high=stock_df['high_price'],
        low=stock_df['low_price'],
        close=stock_df['close_price'],
        dates=stock_df['begins_at']
    )
    fig['layout']['title'] = 'Candlestick plot for {} stocks'.format(stock)
    return fig


if __name__ == '__main__':
    app.run_server()

