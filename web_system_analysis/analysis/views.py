from django.shortcuts import render, redirect
from analysis.models import Price
from django.contrib.auth.models import User

from analysis.forecast import get_forecast

from plotly.offline import plot
from plotly.graph_objs import Scatter

import pandas as pd

item_names = {'gold_price': 'gold', 'oil_price': 'oil', 'copper_price': 'copper'}


def home_page(request):
    return render(request, 'trends/home.html')


def trend(request):
    if request.method == 'GET':
        try:
            item = request.GET['items']
            n_months = int(request.GET['months'])
            method = request.GET['methods']
        except Exception:
            return redirect('/')

    prices = Price
    data = pd.DataFrame(Price.objects.all().values('date', item))
    data.columns = ['date', 'price']

    forecast = get_forecast(data, n_months, method)

    plot_div = plot_data(data, forecast)

    table_div, pred_price, pc_change = create_table(forecast, n_months)

    context = {
        'item': item_names[item],
        'plot_div': plot_div,
        'table_div': table_div,
        'pred_price': pred_price,
        'pc_change': pc_change
    }

    return render(request, 'trends/trend.html', context=context)


def plot_data(original_data: pd.DataFrame, forecast_data: pd.DataFrame):
    fig_actual = Scatter(x=original_data['date'], y=original_data['price'],
                         mode='lines', name='Dynamics',
                         opacity=0.8, marker_color='green')

    if forecast_data['price'].isna().sum() == 0:
        fig_trend = Scatter(x=forecast_data['date'], y=forecast_data['price'],
                            mode='lines', name='Forecast',
                            opacity=0.8, marker_color='red')

        plot_div = plot([fig_actual, fig_trend], output_type='div')

    else:
        plot_div = plot([fig_actual], output_type='div')

    return plot_div


def create_table(forecast_data: pd.DataFrame, n_months: int):
    if forecast_data['price'].isna().sum() == 0:

        n_periods = len(forecast_data) // 30
        monthly_indexes = [i * 30 - 1 for i in range(n_periods - n_months, n_periods + 1)]

        monthly_forecast = forecast_data.iloc[monthly_indexes, :].copy()
        monthly_forecast['date'] = monthly_forecast['date'].apply(lambda x: x.date)

        last_actual_price = monthly_forecast.iloc[0, :]['price']
        last_forecasted_price = round(monthly_forecast.iloc[len(monthly_forecast) - 1, :]['price'], 2)
        pc_change = str(round((last_forecasted_price / last_actual_price - 1) * 100, 2)) + '%'

        monthly_forecast.columns = ['Date', 'Price']
        table = monthly_forecast.iloc[1:, :].to_html(index=False,
                                                     float_format='{:10.2f}'.format,
                                                     classes=['table', 'table-striped'],
                                                     justify='center')


    else:
        table = ''
        last_forecasted_price = 'there is no data'
        pc_change = 'the forecast for the selected period failed, choose another method or change the forecast horizon'

    return table, last_forecasted_price, pc_change
