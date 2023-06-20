from pyecharts.charts import Line, Page, Grid, Bar, Scatter, Scatter3D
import pyecharts.options as opts
from pyecharts.faker import Faker
from pyecharts.charts import *
from pyecharts.globals import ThemeType, RenderType
import pymysql
import pandas as pd
from streamlit_echarts import st_pyecharts
import streamlit as st
import datetime
import streamlit.components.v1 as components
from pyecharts.commons.utils import JsCode
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import numpy as np
from scipy import optimize, stats
import os
import xlwt
from openpyxl import load_workbook
import openpyxl
from dateutil.relativedelta import relativedelta
from scipy.signal import savgol_filter
import sqlite3
from sqlalchemy import create_engine

mysql_setting = {
    'host': "localhost",
    'port': 3306,
    'user': "root",
    'password': '123456',
    'database': 'data',
    'charset': 'utf8'
}

file_setting = {
    'predict': 'D:\Python\Electric\预测价格.xlsx'
}


class Charts:
    def __init__(self, host, port, user, password, database):
        self.connect = pymysql.connect(host=host,
                                       port=port,
                                       user=user,
                                       password=password,
                                       database=database,
                                       charset='utf8')
        self.cursor = self.connect.cursor()

    # 绘制日前市场供需情况:省内负荷、外送、新能源、竞价空间图
    # 绘制市场价格趋势(实时价格、日前价格)
    def draw_info_board(self, df_info):
        line1 = (
            Line(
                init_opts=opts.InitOpts(
                    theme=ThemeType.WALDEN  # 主题
                )
            )
                .add_xaxis(df_info['运行时间'].tolist())
                .add_yaxis('省内负荷', y_axis=df_info['省内负荷'].tolist())
                .add_yaxis('外送', y_axis=df_info['外送'].tolist())
                .add_yaxis('新能源', y_axis=df_info['新能源'].tolist())
                .add_yaxis('竞价空间', y_axis=df_info['竞价空间'].tolist())
                .set_global_opts(
                title_opts=opts.TitleOpts(title='日前市场供需情况', pos_left='30px'),
                datazoom_opts=opts.DataZoomOpts(is_show=True, type_='inside'),
                yaxis_opts=opts.AxisOpts(is_show=True,
                                         axisline_opts=opts.AxisLineOpts(is_show=True),
                                         axistick_opts=opts.AxisTickOpts(is_show=True),
                                         name='MW'),
                toolbox_opts=opts.ToolboxOpts(),
                tooltip_opts=opts.TooltipOpts(trigger='axis')
            )
                .set_series_opts(
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        line2 = (
            Line(
                init_opts=opts.InitOpts(
                    theme=ThemeType.WALDEN,  # 主题
                    height='500px'
                )
            )
                .add_xaxis(df_info['运行时间'].tolist())
                .add_yaxis('实时价格', y_axis=df_info['实时价格'].tolist())
                .add_yaxis('日前价格', y_axis=df_info['日前价格'].tolist())
                .set_global_opts(
                title_opts=opts.TitleOpts(title='市场价格趋势', pos_left='30px'),
                datazoom_opts=opts.DataZoomOpts(is_show=True, type_='inside'),
                toolbox_opts=opts.ToolboxOpts(),
                yaxis_opts=opts.AxisOpts(is_show=True,
                                         axisline_opts=opts.AxisLineOpts(is_show=True),
                                         axistick_opts=opts.AxisTickOpts(is_show=True),
                                         name='元/MWh'),
                tooltip_opts=opts.TooltipOpts(trigger='axis')
            )
                .set_series_opts(
                label_opts=opts.LabelOpts(is_show=False)
            )
        )
        return line1, line2

    # 绘制交易结果（折线图：最高价、最低价、成交均价、加权价、日前价格(压缩平均)；柱状图：总交易量(日均)、交易电量(日均)）
    def draw_trade_result(self, trade_df):
        # option = {
        #     "tooltip": {
        #         "trigger": 'axis'
        #     },
        #     "legend": {
        #         "data": ['最高价', '最低价', '日前价格(压缩平均)','成交均价', '加权价']
        #     },
        #     "xAxis": [
        #         {
        #             "type": 'category',
        #             "data": trade_df['时段'].tolist(),
        #             "axisTick": {
        #                 "alignWithLabel": True
        #             }
        #         }
        #     ],
        #     "yAxis": [
        #         {
        #             "type": 'value',
        #             "axisLabel": {
        #                 "formatter": '{value} '
        #             }
        #         }
        #     ],
        #     "series":[
        #         {
        #             "name":'最高价',
        #             "type":'line',
        #             "data":trade_df['最高价'].tolist(),
        #             "symbolSize":1,
        #             "lineStyle":{
        #                 "width":2
        #             }
        #         },
        #         {
        #             "name": '最低价',
        #             "type": 'line',
        #             "data": trade_df['最低价'].tolist(),
        #             "symbolSize": 1,
        #             "lineStyle": {
        #                 "width": 2
        #             }
        #         },
        #         {
        #             "name": '日前价格(压缩平均)',
        #             "type": 'line',
        #             "data": trade_df['日前价格(压缩平均)'].tolist(),
        #             "symbolSize": 1,
        #             "lineStyle": {
        #                 "width": 2,
        #                 "type": 'dashed'
        #             }
        #         },
        #         {
        #             "name": '成交均价',
        #             "type": 'line',
        #             "data": trade_df['交易电价'].tolist(),
        #             "symbol": 'triangle',
        #             "symbolSize": 15,
        #             "lineStyle": {
        #                 "width": 0
        #             },
        #             "itemStyle":{
        #                 "color": 'black'
        #             }
        #         },
        #         {
        #             "name": '加权价',
        #             "type": 'line',
        #             "data": trade_df['加权价格'].tolist(),
        #             "symbolSize": 1,
        #             "lineStyle": {
        #                 "width": 2,
        #             }
        #         },
        #         {
        #
        #             "name": '加权价',
        #             "type": 'line',
        #             "data": trade_df['加权价格'].tolist(),
        #             "symbolSize": 1,
        #             "lineStyle": {
        #                 "width": 2,
        #             }
        #         },
        #         {
        #             "name": '总交易量(日均)',
        #             "type": 'bar',
        #             "barWidth": '50%',
        #             "data": trade_df['总交易量(日均)'].tolist(),
        #             "z":0
        #         },
        #         {
        #             "name": '交易电量(日均)',
        #             "type": 'bar',
        #             "barWidth": '50%',
        #             "data": trade_df['交易电量(日均)'].tolist(),
        #             "z": 0,
        #             "itemStyle": {
        #                 "normal": {
        #                     "color": """
        #                     function(params) {
        #                         var index_color = params.value;
        #                         if (index_color >= 0){
        #                             return '#fe4365';
        #                         }else {
        #                             return '#25daba';
        #                         }
        #                     }
        #                     """
        #                 }
        #             }
        #         }
        #     ]
        # }
        #

        ##############################################################################################################
        line = Line(init_opts=opts.InitOpts(theme=ThemeType.DARK))  # 主题
        trade_df_rep = trade_df.fillna(0)
        line.add_xaxis(trade_df['时段'].tolist())
        line.add_yaxis('最高价', y_axis=trade_df['最高价'].tolist(), symbol_size=1,
                       linestyle_opts=opts.LineStyleOpts(width=2))  # ,yaxis_index=1
        line.add_yaxis('最低价', y_axis=trade_df['最低价'].tolist(), symbol_size=1,
                       linestyle_opts=opts.LineStyleOpts(width=2))
        line.add_yaxis('日前价格(压缩平均)', y_axis=trade_df['日前价格(压缩平均)'].tolist(), symbol_size=1,
                       linestyle_opts=opts.LineStyleOpts(width=2, type_='dashed'))
        line.add_yaxis('成交均价',
                       y_axis=trade_df['交易电价'].tolist(),
                       symbol='triangle',
                       symbol_size=15,
                       linestyle_opts=opts.LineStyleOpts(is_show=False),
                       itemstyle_opts=opts.ItemStyleOpts(color='black')
                       )
        line.add_yaxis('加权价', y_axis=trade_df['加权价格'].tolist(), symbol_size=1,
                       linestyle_opts=opts.LineStyleOpts(width=2))
        line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

        bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        bar.add_xaxis(trade_df['时段'].tolist())
        bar.add_yaxis('总交易量(日均)', y_axis=trade_df['总交易量(日均)'].tolist(), z=0)
        bar.add_yaxis('交易电量(日均)+', y_axis=trade_df_rep['交易电量(日均)'].mask(trade_df_rep['交易电量(日均)'] <= 0, 0).tolist(), z=0,
                      itemstyle_opts=opts.ItemStyleOpts(color='green'))
        bar.add_yaxis('交易电量(日均)-', y_axis=trade_df_rep['交易电量(日均)'].mask(trade_df_rep['交易电量(日均)'] >= 0, 0).tolist(), z=0,
                      itemstyle_opts=opts.ItemStyleOpts(color='red'))
        # bar.extend_axis(yaxis=opts.AxisOpts(name='电价',position="right", axislabel_opts=opts.LabelOpts(formatter="{value}")
        # ,max_=JsCode("""
        #             function (value) {
        #             if (Math.abs(value.max) > Math.abs(value.min)) {
        #                 return (Math.abs(value.max) * 1.2).toFixed(2);
        #             } else {
        #                 return (Math.abs(value.min) * 1.2).toFixed(2);
        #             }
        #             }
        #             """
        #         ),
        #         min_=JsCode("""
        #         function (value) {
        #             if (Math.abs(value.max) > Math.abs(value.min)) {
        #                 return (-Math.abs(value.max) * 1.2).toFixed(2);
        #             } else {
        #                 return (-Math.abs(value.min) * 1.2).toFixed(2);
        #             }
        #             }
        #         """)
        # ))
        bar.set_global_opts(legend_opts=opts.LegendOpts(type_="scroll", pos_right="0", pos_top='5%', orient="vertical"),
                            title_opts=opts.TitleOpts(pos_left='center',  # text_align='center',
                                                      subtitle='总交易电量:' + str(
                                                          abs(df_trade['交易电量(日均)']).sum().round(3)) + 'MWh',
                                                      subtitle_textstyle_opts=opts.TextStyleOpts(font_size=20),
                                                      title='交易结果(交易日:' + str(trade_df.iloc[0].交易日) + '---运行日:' + str(
                                                          trade_df.iloc[0].运行日) + ')',
                                                      title_textstyle_opts=opts.TextStyleOpts(font_size=23)),
                            tooltip_opts=opts.TooltipOpts(trigger='axis'),
                            # toolbox_opts=opts.ToolboxOpts(),
                            xaxis_opts=opts.AxisOpts(axislabel_opts={"rotate": 50}),
                            yaxis_opts=opts.AxisOpts(is_show=True,  # name='电量',
                                                     axisline_opts=opts.AxisLineOpts(is_show=True),
                                                     axistick_opts=opts.AxisTickOpts(is_show=True)

                                                     #   max_=JsCode("""
                                                     #     function (value) {
                                                     #     if (Math.abs(value.max) > Math.abs(value.min)) {
                                                     #         return (Math.abs(value.max) * 1.2).toFixed(2);
                                                     #     } else {
                                                     #         return (Math.abs(value.min) * 1.2).toFixed(2);
                                                     #     }
                                                     #     }
                                                     #     """
                                                     # ),
                                                     # min_=JsCode("""
                                                     # function (value) {
                                                     #     if (Math.abs(value.max) > Math.abs(value.min)) {
                                                     #         return (-Math.abs(value.max) * 1.2).toFixed(2);
                                                     #     } else {
                                                     #         return (-Math.abs(value.min) * 1.2).toFixed(2);
                                                     #     }
                                                     #     }
                                                     # """)
                                                     ))
        bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

        return bar.overlap(line)

    def draw_profit_result(self, profit_df, mode):
        profit_df.fillna(0, inplace=True)
        if mode == '运行日':
            bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
            bar.add_xaxis(profit_df['小时'].unique().tolist())

            # df = profit_df.groupby('小时').sum()[['盈亏类型', '交易电量(日均)', '交易电费']]
            # df['日前价格(压缩平均)'] = profit_df.groupby('小时').mean()[['日前价格(压缩平均)']]
            # df['偏差处理/主动套利盈亏'] = df['日前价格(压缩平均)']*df['交易电量(日均)'] - df['交易电费']
            # df_1 = df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] != 0) | (df['偏差处理/主动套利盈亏'] < 0), 0).tolist()
            # bar.add_yaxis('偏差处理盈亏+', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] != 0) | (df['偏差处理/主动套利盈亏'] < 0), 0).round(3).tolist(), itemstyle_opts=opts.ItemStyleOpts(color='blue'))
            # bar.add_yaxis('偏差处理盈亏-', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] != 0) | (df['偏差处理/主动套利盈亏'] > 0), 0).round(3).tolist(), itemstyle_opts=opts.ItemStyleOpts(color='red'))
            # bar.add_yaxis('主动套利盈亏+', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] == 0) | (df['偏差处理/主动套利盈亏'] < 0), 0).round(3).tolist(), itemstyle_opts=opts.ItemStyleOpts(color='green'))
            # bar.add_yaxis('主动套利盈亏-', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] == 0) | (df['偏差处理/主动套利盈亏'] > 0), 0).round(3).tolist(), itemstyle_opts=opts.ItemStyleOpts(color='yellow'))
            # bar.set_global_opts(legend_opts=opts.LegendOpts(type_="scroll", pos_right="0",pos_top='5%',orient="vertical"),
            #                      title_opts=opts.TitleOpts(title_textstyle_opts=opts.TextStyleOpts(font_size=23),pos_left='center', title='盈亏结果(运行日:'+ str(profit_df.iloc[0].运行日)+')',
            #                                                subtitle = '总盈亏:'+ str((df['偏差处理/主动套利盈亏'].sum()/10000).round(3)) + '万元    '
            #                                                           +'偏差处理盈亏:' + str(df['偏差处理/主动套利盈亏'][df['盈亏类型'] == 0].sum().round(1)) + '元    '
            #                                                           +'主动套利盈亏:' + str(df['偏差处理/主动套利盈亏'][df['盈亏类型'] > 0].sum().round(1)) + '元',
            df = profit_df.groupby('小时').sum()[['偏差处理/主动套利盈亏', '盈亏类型']]
            bar.add_yaxis('偏差处理盈亏+', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] != 0) | (df['偏差处理/主动套利盈亏'] < 0), 0).tolist(),
                          itemstyle_opts=opts.ItemStyleOpts(color='    #4169E1'))
            bar.add_yaxis('偏差处理盈亏-', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] != 0) | (df['偏差处理/主动套利盈亏'] > 0), 0).tolist(),
                          itemstyle_opts=opts.ItemStyleOpts(color='red'))
            bar.add_yaxis('主动套利盈亏+', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] == 0) | (df['偏差处理/主动套利盈亏'] < 0), 0).tolist(),
                          itemstyle_opts=opts.ItemStyleOpts(color='    #87CEFA'))
            bar.add_yaxis('主动套利盈亏-', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] == 0) | (df['偏差处理/主动套利盈亏'] > 0), 0).tolist(),
                          itemstyle_opts=opts.ItemStyleOpts(color='pink'))
            bar.set_global_opts(
                legend_opts=opts.LegendOpts(type_="scroll", pos_right="0", pos_top='5%', orient="vertical"),
                title_opts=opts.TitleOpts(title_textstyle_opts=opts.TextStyleOpts(font_size=23),
                                          pos_left='center',
                                          title='盈亏结果(运行日:' + str(profit_df.iloc[0].运行日) + ')',
                                          subtitle='总盈亏:' + str(
                                              profit_df['总盈亏(万元)'].sum().round(3)) + '万元    '
                                                   + '偏差处理盈亏:' + str(
                                              profit_df['偏差处理/主动套利盈亏'][df_profit['盈亏类型'] == 0].sum().round(
                                                  1)) + '元    '
                                                   + '主动套利盈亏:' + str(
                                              profit_df['偏差处理/主动套利盈亏'][df_profit['盈亏类型'] == 1].sum().round(
                                                  1)) + '元',
                                          subtitle_textstyle_opts=opts.TextStyleOpts(font_size=20)),
                tooltip_opts=opts.TooltipOpts(trigger='axis'),
                # toolbox_opts=opts.ToolboxOpts(),
                xaxis_opts=opts.AxisOpts(),
                yaxis_opts=opts.AxisOpts(is_show=True,
                                         axisline_opts=opts.AxisLineOpts(is_show=True),
                                         axistick_opts=opts.AxisTickOpts(is_show=True)))
            bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        elif mode == '交易日-运行日':
            bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
            bar.add_xaxis(profit_df['小时'].unique().tolist())
            df = profit_df
            bar.add_yaxis('偏差处理盈亏+', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] != 0) | (df['偏差处理/主动套利盈亏'] < 0), 0).tolist(),
                          itemstyle_opts=opts.ItemStyleOpts(color='    #4169E1'))
            bar.add_yaxis('偏差处理盈亏-', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] != 0) | (df['偏差处理/主动套利盈亏'] > 0), 0).tolist(),
                          itemstyle_opts=opts.ItemStyleOpts(color='red'))
            bar.add_yaxis('主动套利盈亏+', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] == 0) | (df['偏差处理/主动套利盈亏'] < 0), 0).tolist(),
                          itemstyle_opts=opts.ItemStyleOpts(color='    #87CEFA'))
            bar.add_yaxis('主动套利盈亏-', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] == 0) | (df['偏差处理/主动套利盈亏'] > 0), 0).tolist(),
                          itemstyle_opts=opts.ItemStyleOpts(color='pink'))
            bar.set_global_opts(
                legend_opts=opts.LegendOpts(type_="scroll", pos_right="0", pos_top='5%', orient="vertical"),
                title_opts=opts.TitleOpts(title_textstyle_opts=opts.TextStyleOpts(font_size=23), pos_left='center',
                                          title='盈亏结果(交易日:' + str(profit_df.iloc[0].交易日) + '---运行日:' + str(
                                              profit_df.iloc[0].运行日) + ')',
                                          subtitle='总盈亏:' + str(profit_df['总盈亏(万元)'].sum().round(3)) + '万元    '
                                                   + '偏差处理盈亏:' + str(
                                              profit_df['偏差处理/主动套利盈亏'][df_profit['盈亏类型'] == 0].sum().round(3)) + '元    '
                                                   + '主动套利盈亏:' + str(
                                              profit_df['偏差处理/主动套利盈亏'][df_profit['盈亏类型'] == 1].sum().round(3)) + '元',
                                          subtitle_textstyle_opts=opts.TextStyleOpts(font_size=20)),
                # tooltip_opts=opts.TooltipOpts(trigger='axis'),
                # toolbox_opts=opts.ToolboxOpts(),
                xaxis_opts=opts.AxisOpts(),
                yaxis_opts=opts.AxisOpts(is_show=True,
                                         axisline_opts=opts.AxisLineOpts(is_show=True),
                                         axistick_opts=opts.AxisTickOpts(is_show=True)))
            bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        return bar

    # 绘制日前或实时价格
    def draw_price(self, df_price, is_real, is_compress, begin_date, end_date):
        line = Line(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))  # 主题
        line.add_xaxis(df_price['时间'].unique().tolist())
        date_list = pd.date_range(begin_date, end_date, freq='D').strftime("%Y-%m-%d").to_list()

        if is_real & is_compress:
            for date in date_list:
                line.add_yaxis(date, y_axis=df_price['实时价格(压缩)'][
                    pd.to_datetime(df_price['运行日期']) == pd.to_datetime(date)].tolist())
        elif is_real & (not is_compress):
            for date in date_list:
                line.add_yaxis(date, y_axis=df_price['实时价格'][
                    pd.to_datetime(df_price['运行日期']) == pd.to_datetime(date)].tolist())
        elif (not is_real) & is_compress:
            for date in date_list:
                line.add_yaxis(date, y_axis=df_price['日前价格(压缩)'][
                    pd.to_datetime(df_price['运行日期']) == pd.to_datetime(date)].tolist())
        elif (not is_real) & (not is_compress):
            for date in date_list:
                line.add_yaxis(date, y_axis=df_price['日前价格'][
                    pd.to_datetime(df_price['运行日期']) == pd.to_datetime(date)].tolist())

        line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        line.set_global_opts(tooltip_opts=opts.TooltipOpts(trigger='axis'),
                             yaxis_opts=opts.AxisOpts(is_show=True,
                                                      axisline_opts=opts.AxisLineOpts(is_show=True),
                                                      axistick_opts=opts.AxisTickOpts(is_show=True),
                                                      name='元/MWh'),
                             toolbox_opts=opts.ToolboxOpts())

        return line

    # 绘制日前实时价格对比
    def draw_price_compare(self, df_price, is_compress, begin_date, end_date):
        line1 = Line(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))  # 主题
        line2 = Line(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))  # 主题
        date_list = pd.date_range(begin_date, end_date, freq='D').strftime("%Y-%m-%d").to_list()
        line1.add_xaxis(date_list)
        line2.add_xaxis(df_price['时间'].unique().tolist())
        if not is_compress:
            line1.add_yaxis('实时价格', df_price.groupby('运行日期')['实时价格'].mean().round(2).tolist(),
                            markpoint_opts=opts.MarkPointOpts(
                                data=[opts.MarkPointItem(type_='max', symbol='pin', symbol_size=80)]))
            line1.add_yaxis('日前价格', df_price.groupby('运行日期')['日前价格'].mean().round(2).tolist(),
                            markpoint_opts=opts.MarkPointOpts(
                                data=[opts.MarkPointItem(type_='max', symbol='pin', symbol_size=80)]))
            line2.add_yaxis('实时价格', df_price.groupby('时间')['实时价格'].mean().round(2).tolist(),
                            markpoint_opts=opts.MarkPointOpts(
                                data=[opts.MarkPointItem(type_='max', symbol='pin', symbol_size=80)]))
            line2.add_yaxis('日前价格', df_price.groupby('时间')['日前价格'].mean().round(2).tolist(),
                            markpoint_opts=opts.MarkPointOpts(
                                data=[opts.MarkPointItem(type_='max', symbol='pin', symbol_size=80)]))
        else:
            line1.add_yaxis('实时价格(压缩)', df_price.groupby('运行日期')['实时价格(压缩)'].mean().round(2).tolist(),
                            markpoint_opts=opts.MarkPointOpts(
                                data=[opts.MarkPointItem(type_='max', symbol='pin', symbol_size=80)]))
            line1.add_yaxis('日前价格(压缩)', df_price.groupby('运行日期')['日前价格(压缩)'].mean().round(2).tolist(),
                            markpoint_opts=opts.MarkPointOpts(
                                data=[opts.MarkPointItem(type_='max', symbol='pin', symbol_size=80)]))
            line2.add_yaxis('实时价格(压缩)', df_price.groupby('时间')['实时价格(压缩)'].mean().round(2).tolist(),
                            markpoint_opts=opts.MarkPointOpts(
                                data=[opts.MarkPointItem(type_='max', symbol='pin', symbol_size=80)]))
            line2.add_yaxis('日前价格(压缩)', df_price.groupby('时间')['日前价格(压缩)'].mean().round(2).tolist(),
                            markpoint_opts=opts.MarkPointOpts(
                                data=[opts.MarkPointItem(type_='max', symbol='pin', symbol_size=80)]))
        line1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        line1.set_global_opts(tooltip_opts=opts.TooltipOpts(trigger='axis'),
                              yaxis_opts=opts.AxisOpts(is_show=True,
                                                       axisline_opts=opts.AxisLineOpts(is_show=True),
                                                       axistick_opts=opts.AxisTickOpts(is_show=True),
                                                       name='元/MWh'),
                              toolbox_opts=opts.ToolboxOpts())
        line2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        line2.set_global_opts(tooltip_opts=opts.TooltipOpts(trigger='axis'),
                              yaxis_opts=opts.AxisOpts(is_show=True,
                                                       axisline_opts=opts.AxisLineOpts(is_show=True),
                                                       axistick_opts=opts.AxisTickOpts(is_show=True),
                                                       name='元/MWh'),
                              toolbox_opts=opts.ToolboxOpts())

        return line1, line2

    # 绘制日前价格与竞价空间
    def draw_price_jjkj(self, df_compete, is_compress):
        df_compete['运行时间'] = df_compete['运行日期'].map(str) + ' ' + df_compete['时间'].map(str)
        # df_compete['竞价容量比%'] = df_compete['竞价容量比'].apply(lambda x: '%.2f%%' % (x * 100))
        df_compete['竞价容量比%'] = df_compete['竞价容量比'].apply(lambda x: x * 100).round(2)
        bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        bar.add_xaxis(df_compete['运行时间'].tolist())
        bar.add_yaxis('竞价空间(日前)', y_axis=df_compete['竞价空间'].tolist(), z=0)
        bar.extend_axis(
            yaxis=opts.AxisOpts(min_=0, max_=100, position="right", axislabel_opts=opts.LabelOpts(formatter="{value}%"),
                                interval=10, axisline_opts=opts.AxisLineOpts(is_show=True)))
        bar.extend_axis(
            yaxis=opts.AxisOpts(min_=0, max_=1500, position="right", axislabel_opts=opts.LabelOpts(formatter="{value}"),
                                offset=80, axisline_opts=opts.AxisLineOpts(is_show=True)))
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title='价格与竞价空间趋势'),
            datazoom_opts=opts.DataZoomOpts(is_show=True, type_='inside'),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger='axis')
        )
        bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

        line1 = Line(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        line1.add_xaxis(df_compete['运行时间'].tolist())
        if is_compress == '压缩':
            line1.add_yaxis('日前价格(压缩)', y_axis=df_compete['日前价格(压缩)'].tolist(), yaxis_index=2)
        elif is_compress == '不压缩':
            line1.add_yaxis('日前价格', y_axis=df_compete['日前价格'].tolist(), yaxis_index=2)
        line1.add_yaxis('竞价容量比', y_axis=df_compete['竞价容量比%'].tolist(), yaxis_index=1)
        line1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

        return bar.overlap(line1)

    # 绘制竞价空间与日前价格散点图
    def draw_jjkj_curve(self, df_compete, date_list):
        scat1 = Scatter(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        for date in date_list:
            scat1.add_xaxis(
                df_compete['竞价空间'][pd.to_datetime(df_compete['运行日期']) == pd.to_datetime(date)].unique().tolist())
            scat1.add_yaxis(date, y_axis=df_compete['日前价格'][
                pd.to_datetime(df_compete['运行日期']) == pd.to_datetime(date)].tolist(), symbol_size=10,
                            label_opts=opts.LabelOpts(is_show=False))
        scat1.set_global_opts(
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="right", orient="vertical"),
            title_opts=opts.TitleOpts(title='竞价空间(日前)-日前价格', pos_left='30px'),
            yaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True)),
            xaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True), min_=5000),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger_on='mousemove|click', axis_pointer_type='cross', formatter=JsCode(
                "function (params) {return '日期:'+params.seriesName + '<br/>' + '日前价格:'+ params.value[1] + '<br/>'+ '竞价空间(日前):' + params.value[0] + '<br/>';}"))
        )

        df_compete['竞价容量比%'] = df_compete['竞价容量比'].apply(lambda x: x * 100).round(2)
        scat2 = Scatter(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        for date in date_list:
            scat2.add_xaxis(
                df_compete['竞价容量比%'][pd.to_datetime(df_compete['运行日期']) == pd.to_datetime(date)].unique().tolist())
            scat2.add_yaxis(date, y_axis=df_compete['日前价格'][
                pd.to_datetime(df_compete['运行日期']) == pd.to_datetime(date)].tolist(), symbol_size=10,
                            label_opts=opts.LabelOpts(is_show=False))
        scat2.set_global_opts(
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="right", orient="vertical"),
            title_opts=opts.TitleOpts(title='竞价容量比-日前价格', pos_left='30px'),
            yaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True)),
            xaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True), min_=0, max_=100,
                                     axislabel_opts=opts.LabelOpts(formatter="{value}%")),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger_on='mousemove|click', axis_pointer_type='cross', formatter=JsCode(
                "function (params) {return '日期:'+params.seriesName + '<br/>' + '日前价格:'+ params.value[1] + '<br/>'+ '竞价容量比:' + params.value[0] + '%<br/>';}"
            ))
        )

        scat3 = Scatter3D(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        for date in date_list:
            data = list(zip(df_compete['竞价容量比%'][pd.to_datetime(df_compete['运行日期']) == pd.to_datetime(date)].tolist(),
                            df_compete['竞价空间'][pd.to_datetime(df_compete['运行日期']) == pd.to_datetime(date)].tolist(),
                            df_compete['日前价格'][pd.to_datetime(df_compete['运行日期']) == pd.to_datetime(date)].tolist()))
            scat3.add(series_name=date, data=data,
                      xaxis3d_opts=opts.Axis3DOpts(
                          name='竞价容量比',
                          type_="value",
                          axislabel_opts=opts.LabelOpts(formatter="{value}%")
                      ),
                      yaxis3d_opts=opts.Axis3DOpts(
                          name='竞价空间(日前)',
                          type_="value",
                      ),
                      zaxis3d_opts=opts.Axis3DOpts(
                          name='日前价格',
                          type_="value",
                      ),
                      grid3d_opts=opts.Grid3DOpts(is_rotate=True)  # width=100, height=100, depth=100
                      )
        scat3.set_global_opts(legend_opts=opts.LegendOpts(type_="scroll", pos_left="right", orient="vertical"),
                              title_opts=opts.TitleOpts(title='竞价空间(日前)-竞价容量比-日前价格', pos_left='30px'),
                              toolbox_opts=opts.ToolboxOpts(),
                              tooltip_opts=opts.TooltipOpts(
                                  formatter=JsCode(
                                      "function (params) {return '日期:'+params.seriesName + '<br/>' + '日前价格:'+ params.value[2] + '<br/>' + '竞价空间(日前):' + params.value[1] + '<br/>'+ '竞价容量比:' + params.value[0] + '%<br/>';}"
                                  )
                              ))
        return scat1, scat2, scat3

    def draw_profit_price(self, df_reference):
        # df_reference.index = list(range(1, 97))
        line = (
            Line(
                init_opts=opts.InitOpts(
                    theme=ThemeType.WALDEN  # 主题
                )
            )
                .add_xaxis(df_reference.index.tolist())
        )
        for i in range(1, df_reference.shape[1], 2):
            line.add_yaxis(df_reference.columns[i], df_reference.iloc[:, i], is_smooth=True, is_symbol_show=False)
        line.set_global_opts(
            title_opts=opts.TitleOpts(title='价格预测', pos_left='30px'),
            datazoom_opts=opts.DataZoomOpts(is_show=True, type_='inside'),
            yaxis_opts=opts.AxisOpts(is_show=True,
                                     axisline_opts=opts.AxisLineOpts(is_show=True),
                                     axistick_opts=opts.AxisTickOpts(is_show=True),
                                     ),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger='axis')
        )
        line.set_series_opts(
            label_opts=opts.LabelOpts(is_show=False)
        )

        scat = Scatter(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        scat.add_xaxis(df_reference.iloc[:, 0].apply(lambda x: x * 100).round(2).tolist())
        scat.add_yaxis(df_reference.columns[1], df_reference.iloc[:, 1].tolist(),
                       label_opts=opts.LabelOpts(is_show=False))
        scat.set_global_opts(title_opts=opts.TitleOpts(title='竞价容量比-日前价格', pos_left='30px'),
                             yaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True)),
                             xaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True),
                                                      min_=0, max_=100,
                                                      axislabel_opts=opts.LabelOpts(formatter="{value}%")),
                             toolbox_opts=opts.ToolboxOpts(),
                             tooltip_opts=opts.TooltipOpts(trigger_on='mousemove|click', axis_pointer_type='cross',
                                                           formatter=JsCode(
                                                               "function (params) {return '日期:'+params.seriesName + '<br/>' + '日前价格:'+ params.value[1] + '<br/>'+ '竞价容量比:' + params.value[0] + '%<br/>';}"
                                                           )))

        return scat, line

    # 绘制日前价格复盘
    def draw_reverse(self, df_value):
        line = (
            Line(
                init_opts=opts.InitOpts(
                    theme=ThemeType.WALDEN  # 主题
                )
            )
                .add_xaxis(df_value.index.tolist())
        )
        for col in df_value.columns:
            line.add_yaxis(col, df_value[col].tolist(), is_smooth=True, is_symbol_show=False)
        line.set_global_opts(
            title_opts=opts.TitleOpts(title='价格预测', pos_left='30px'),
            datazoom_opts=opts.DataZoomOpts(is_show=True, type_='inside'),
            yaxis_opts=opts.AxisOpts(is_show=True,
                                     axisline_opts=opts.AxisLineOpts(is_show=True),
                                     axistick_opts=opts.AxisTickOpts(is_show=True),
                                     ),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger='axis')
        )
        line.set_series_opts(
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    # 一个输入序列，4个未知参数，2个分段函数
    def piecewise_linear(x, x0, y0, k1, k2):
        # x<x0 ⇒ lambda x: k1*x + y0 - k1*x0
        # x>=x0 ⇒ lambda x: k2*x + y0 - k2*x0
        return np.piecewise(x, [x < x0, x >= x0], [lambda x: k1 * x + y0 - k1 * x0,
                                                   lambda x: k2 * x + y0 - k2 * x0])

    def piecewise_linear3(x, x0, x1, y0, y1, k0, k1):
        return np.piecewise(x, [x <= x0, np.logical_and(x0 < x, x <= x1), x > x1],
                            [lambda x: k0 * (x - x0) + y0,  # 根据点斜式构建函数
                             lambda x: (x - x0) * (y1 - y0) / (x1 - x0) + y0,  # 根据两点式构建函数
                             lambda x: k1 * (x - x1) + y1])

    def draw_modify_price(self, df_reference, refer_datelist, order):
        scat = Scatter(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        scat.add_xaxis(df_reference.iloc[:, 0].tolist())
        scat.add_yaxis(df_reference.columns[1], df_reference.iloc[:, 1].tolist(), symbol_size=5, symbol='triangle',
                       itemstyle_opts=opts.ItemStyleOpts(color='black'),
                       label_opts=opts.LabelOpts(is_show=False))
        n = 2
        x_listData = list()
        y_listData = list()
        for i in refer_datelist:
            x_oldData = df_reference.iloc[:, n].tolist()
            y_oldData = df_reference.iloc[:, n + 1].tolist()
            x_listData.extend(x_oldData)
            y_listData.extend(y_oldData)

            scat.add_xaxis(x_oldData)
            scat.add_yaxis(df_reference.columns[n + 1], y_oldData, symbol_size=7,
                           label_opts=opts.LabelOpts(is_show=False))
            n += 3

        scat.set_global_opts(
            title_opts=opts.TitleOpts(title='竞价容量比-日前价格', pos_left='30px'),
            yaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True)),
            xaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True), min_=0, max_=100,
                                     axislabel_opts=opts.LabelOpts(formatter="{value}%")),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger_on='mousemove|click', axis_pointer_type='cross', formatter=JsCode(
                "function (params) {return '日期:'+params.seriesName + '<br/>' + '日前价格:'+ params.value[1] + '<br/>'+ '竞价容量比:' + params.value[0] + '%<br/>';}"
            ))
        )

        if (len(x_listData) != 0) & (len(y_listData) != 0):
            data = list(zip(x_listData, y_listData))
            data.sort(key=lambda x: x[0])
            df_data = pd.DataFrame(data=data, columns=['x', 'y'])
            df_data['y_diff1'] = df_data['y'].diff(1)
            p = np.polyfit(x_listData, y_listData, order)
            y_fit = np.polyval(p, x_listData)
            line1 = (
                Line()
                    .add_xaxis(x_listData)
                    .add_yaxis('拟合曲线', y_fit, is_smooth=True, is_symbol_show=False)
            )
            scat.overlap(line1)

            line2 = (
                Line()
                    .add_xaxis(df_reference.index.tolist())
                    .add_yaxis(df_reference.columns[1], df_reference.iloc[:, 1].tolist(), is_smooth=True,
                               is_symbol_show=False)
            )
            for i in refer_datelist:
                y_predict = np.polyval(p, df_reference[i.strftime('%Y-%m-%d')].tolist())
                line2.add_yaxis("{}预测价格".format(i), np.maximum(y_predict.round(2), 0), is_smooth=True,
                                is_symbol_show=False)

            line2.set_global_opts(
                title_opts=opts.TitleOpts(title='价格预测', pos_left='30px'),
                datazoom_opts=opts.DataZoomOpts(is_show=True, type_='inside'),
                yaxis_opts=opts.AxisOpts(is_show=True,
                                         axisline_opts=opts.AxisLineOpts(is_show=True),
                                         axistick_opts=opts.AxisTickOpts(is_show=True),
                                         ),
                toolbox_opts=opts.ToolboxOpts(),
                tooltip_opts=opts.TooltipOpts(trigger='axis')
            )
            line2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

        # 用已有的 (x, y) 去拟合 piecewise_linear 分段函数
        # p, e = optimize.curve_fit(self.piecewise_linear, x_oldData, y_oldData)
        # 用已有的 (x, y) 去拟合 piecewise_linear3 分段函数
        # p, e = optimize.curve_fit(self.piecewise_linear3, x_oldData, y_oldData, bounds=(0, [16, 16, 120, 120, 10, 10]))
        # yinterp = np.interp(x_oldData, x_oldData, y_oldData)
        # xd = np.linspace(0, 15, 100)
        # line2 = (
        #     Line()
        #         .add_xaxis(xd)
        #         .add_yaxis('分段拟合曲线', self.piecewise_linear(xd, *p), is_smooth=True, is_symbol_show=False)
        # )

        return scat, line2

    def moving_average(self, interval, windowsize):
        window = np.ones(int(windowsize)) / float(windowsize)
        re = np.convolve(interval, window, 'same')
        return re

    #预测未来x天数据
    def draw_price_predict(self, df_sim, df_predict):
        line = Line(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        line.add_xaxis(list(range(0, 96)))
        line.add_yaxis(df_sim.columns[0], df_sim.iloc[:, 0].tolist(), is_smooth=True,is_symbol_show=False, linestyle_opts=opts.LineStyleOpts(type_='dashed', color='black'))
        line.set_global_opts(
            title_opts=opts.TitleOpts(title='96点竞价容量比', pos_left='30px'),
            datazoom_opts=opts.DataZoomOpts(is_show=True, type_='inside'),
            yaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True),
                                     axisline_opts=opts.AxisLineOpts(is_show=True),
                                     axistick_opts=opts.AxisTickOpts(is_show=True), min_=0, max_=100,
                                     axislabel_opts=opts.LabelOpts(formatter="{value}%")),
            tooltip_opts=opts.TooltipOpts(trigger='axis'),
            legend_opts=opts.LegendOpts(
                type_='scroll',
                is_show=True,
                pos_left='right',
                orient='vertical',
            )
        )
        line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

        scat = Scatter(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        scat.add_xaxis(df_predict.iloc[:, 0].tolist())
        scat.add_yaxis(df_predict.columns[1].replace('日前价格', ''), df_predict.iloc[:, 1].tolist(),label_opts=opts.LabelOpts(is_show=False))
        scat.set_global_opts(
            title_opts=opts.TitleOpts(title='竞价容量比-日前价格', pos_left='30px'),
            yaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True)),
            xaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True), min_=0, max_=100,
                                     axislabel_opts=opts.LabelOpts(formatter="{value}%")),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger_on='mousemove|click', axis_pointer_type='cross', formatter=JsCode(
                "function (params) {return '日期:'+params.seriesName + '<br/>' + '日前价格:'+ params.value[1] + '<br/>'+ '竞价容量比:' + params.value[0] + '%<br/>';}"
            ))
        )

        x_listData = df_predict.iloc[:, 0].tolist()
        y_listData = df_predict.iloc[:, 1].tolist()
        for i in range(1, len(df_sim.columns), 2):
            line.add_yaxis(df_sim.columns[i], df_sim.iloc[:, i].tolist(), is_smooth=True, is_symbol_show=False)
            x_data = df_sim.iloc[:,i]
            y_data = df_sim.iloc[:, i+1]
            y_seriesName = df_sim.columns[i + 1].replace('日前价格', '')
            scat.add_xaxis(x_data)
            scat.add_yaxis(y_seriesName, y_data, label_opts=opts.LabelOpts(is_show=False))
            x_listData.extend(x_data)
            y_listData.extend(y_data)

        df_xy = pd.DataFrame(list(zip(x_listData, y_listData)), columns=['竞价容量比', '日前价格'])
        df_xy.sort_values(by='竞价容量比')
        y_predict = pd.Series(0, index=list(range(0, 96)))
        for j in range(0, 96):
            find_data = df_sim.iloc[j,0]
            reference_df = df_xy.iloc[:, 0]
            y_predict[j] = df_xy.iloc[(reference_df - find_data).abs().sort_values().index[0], 1]
        y_oldPredict = y_predict
        y_predict = savgol_filter(y_predict, 15, 2, mode='nearest')
        y_predict = np.where(y_predict > 0, y_predict, 0)

        line2 = (
            Line()
                .add_xaxis(list(range(0, 96)))
                .add_yaxis(df_predict_percent.name.replace('竞价容量比', '预测价格'), y_predict.round(2), is_smooth=True,is_symbol_show=False)
                .add_yaxis(df_predict_percent.name.replace('竞价容量比', '原始预测价格'), y_oldPredict.round(2), is_smooth=True,linestyle_opts=opts.LineStyleOpts(type_='dashed', color='black'),is_symbol_show=False)
        )
        line2.set_global_opts(
            title_opts=opts.TitleOpts(title='预测价格', pos_left='30px'),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger='axis')
        )
        line2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        return line, scat, line2

    #根据相似日复盘预测价格
    def draw_price_similar(self, df_match_date, df_predict_percent, df_refer, sim_order):
        df_match_date.index = list(range(0, 96))
        df_match_date.iloc[:, 0] = df_match_date.iloc[:, 0].apply(lambda x: x * 100).round(2)
        df_predict_percent = df_predict_percent.apply(lambda x: x * 100).round(2)
        df_refer.iloc[:,[i%2==0 for i in range(len(df_refer.columns))]] = df_refer.iloc[:,[i%2==0 for i in range(len(df_refer.columns))]].apply(lambda x: x * 100).round(2)
        line = Line(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        line.add_xaxis(list(range(0, 96)))
        line.add_yaxis(df_match_date.columns[0], df_match_date.iloc[:, 0].tolist(), is_smooth=True, is_symbol_show=False,linestyle_opts=opts.LineStyleOpts(type_='dashed', color='black'))
        line.add_yaxis(df_predict_percent.name, df_predict_percent.tolist(), is_smooth=True, is_symbol_show=False,linestyle_opts=opts.LineStyleOpts(color='black'))
        line.add_yaxis(df_refer.columns[0], df_refer.iloc[:, 0].tolist(), is_smooth=True, is_symbol_show=False)
        line.set_global_opts(
            title_opts=opts.TitleOpts(title='96点竞价容量比', pos_left='30px'),
            datazoom_opts=opts.DataZoomOpts(is_show=True, type_='inside'),
            yaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True),
                                     axisline_opts=opts.AxisLineOpts(is_show=True),
                                     axistick_opts=opts.AxisTickOpts(is_show=True), min_=0, max_=100,
                                     axislabel_opts=opts.LabelOpts(formatter="{value}%")),
            tooltip_opts=opts.TooltipOpts(trigger='axis'),
            legend_opts=opts.LegendOpts(
                type_='scroll',
                is_show=True,
                pos_left='right',
                orient='vertical',
            )
        )
        line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

        scat = Scatter(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        scat.add_xaxis(df_match_date.iloc[:, 0].tolist())
        scat.add_yaxis(df_match_date.columns[1].replace('日前价格', ''), df_match_date.iloc[:, 1].tolist(), symbol_size=5, symbol='triangle',itemstyle_opts=opts.ItemStyleOpts(color='black'),label_opts=opts.LabelOpts(is_show=False))

        x_listData = list()
        y_listData = list()
        for i in range(0, len(df_refer.columns), 2):
            x_data = df_refer.iloc[:, i].tolist()
            y_data = df_refer.iloc[:, i + 1].tolist()
            x_listData.extend(x_data)
            y_listData.extend(y_data)
            line.add_yaxis(df_refer.columns[i], x_data, is_smooth=True, is_symbol_show=False)

            series_name = df_refer.columns[i + 1].replace('日前价格', '')
            scat.add_xaxis(x_data)
            scat.add_yaxis(series_name, y_data, label_opts=opts.LabelOpts(is_show=False))

        data = list(zip(x_listData, y_listData))
        data.sort(key=lambda x: x[0])
        df_data = pd.DataFrame(data=data, columns=['x', 'y'])
        df_data['y_diff1'] = df_data['y'].diff(1)
        df_data.sort_values(by='y_diff1', ascending=False, inplace=True)
        threshhold = 0
        if df_data.iloc[0, 2] > 80:
            threshhold = df_data.iloc[0, 0]

        line1 = Line()
        if threshhold != 0:
            df_data.sort_values(by='x', inplace=True)
            x1_listData = df_data['x'][df_data['x']<threshhold]
            y1_listData = df_data['y'][df_data['x']<threshhold]
            x2_listData = df_data['x'][df_data['x']>=threshhold]
            y2_listData = df_data['y'][df_data['x']>=threshhold]
            p1 = np.polyfit(x1_listData, y1_listData, sim_order)
            p2 = np.polyfit(x2_listData, y2_listData, sim_order)
            df_predict = pd.DataFrame(df_predict_percent)
            df_predict['日前价格'] = df_predict.iloc[:,0].apply(lambda x: np.polyval(p1, x) if x < threshhold else np.polyval(p2, x))
            y_predict = df_predict['日前价格']
            y_fit1 = np.polyval(p1, x1_listData)
            y_fit2 = np.polyval(p2, x2_listData)
            line1.add_xaxis(x1_listData)
            line1.add_yaxis('拟合曲线1', y_fit1, is_smooth=True, is_symbol_show=False,linestyle_opts=opts.LineStyleOpts(color='black', width=3))
            line1.add_xaxis(x2_listData)
            line1.add_yaxis('拟合曲线2', y_fit2, is_smooth=True, is_symbol_show=False,linestyle_opts=opts.LineStyleOpts(color='black', width=3))
        elif threshhold == 0:
            p = np.polyfit(x_listData, y_listData, sim_order)
            y_fit = np.polyval(p, x_listData)
            y_predict = np.polyval(p, df_predict_percent.tolist())
            line1.add_xaxis(x_listData)
            line1.add_yaxis('拟合曲线1', y_fit, is_smooth=True, is_symbol_show=False,linestyle_opts=opts.LineStyleOpts(color='black', width=3))

        scat.overlap(line1)
        scat.set_global_opts(
            title_opts=opts.TitleOpts(title='竞价容量比-日前价格', pos_left='30px'),
            yaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True)),
            xaxis_opts=opts.AxisOpts(type_='value', splitline_opts=opts.SplitLineOpts(is_show=True), min_=0, max_=100,
                                     axislabel_opts=opts.LabelOpts(formatter="{value}%")),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger_on='mousemove|click', axis_pointer_type='cross', formatter=JsCode(
                "function (params) {return '日期:'+params.seriesName + '<br/>' + '日前价格:'+ params.value[1] + '<br/>'+ '竞价容量比:' + params.value[0] + '%<br/>';}"
            ))
        )

        df_xy = pd.DataFrame(list(zip(x_listData, y_listData)), columns=['竞价容量比', '日前价格'])
        df_xy.sort_values(by='竞价容量比')
        df_predict_percent['日前价格'] = ""
        y_predict = pd.Series(0,index = list(range(0, 96)))
        for j in range(0, 96):
            find_data = df_predict_percent[j]
            reference_df = df_xy.iloc[:, 0]
            y_predict[j] = df_xy.iloc[(reference_df - find_data).abs().sort_values().index[0], 1]
        y_oldPredict = y_predict
        # y_predict = self.moving_average(y_predict, 10)
        y_predict = savgol_filter(y_predict, 15, 2, mode='nearest')
        y_predict = np.where(y_predict>0, y_predict, 0)
        y_predict_percent = pd.concat([df_match_date.iloc[:, 1], pd.Series(y_predict)], axis=1, ignore_index=True)
        y_predict_percent['percent'] = 1-abs(y_predict_percent.iloc[:, 0]-y_predict_percent.iloc[:, 1])/y_predict_percent.iloc[:, 0]
        y_predict_percent['percent'] = y_predict_percent['percent'].apply(lambda x: x * 100).round(2)
        line2 = (
            Line()
                .add_xaxis(list(range(0, 96)))
                .add_yaxis(df_match_date.columns[1].replace('日前价格', ''), df_match_date.iloc[:, 1].tolist(), is_smooth=True,is_symbol_show=False)
                .add_yaxis(df_predict_percent.name.replace('竞价容量比', '预测价格'), y_predict.round(2), is_smooth=True,is_symbol_show=False)
                .add_yaxis(df_predict_percent.name.replace('竞价容量比', '原始预测价格'), y_oldPredict.round(2), is_smooth=True,linestyle_opts=opts.LineStyleOpts(type_='dashed', color='black'),
                           is_symbol_show=False)
        )
        line2.set_global_opts(
            title_opts=opts.TitleOpts(title='预测价格', pos_left='30px', subtitle='平均准确率:{}% 最高:{}% 最低:{}%'.format(round(y_predict_percent['percent'].mean(), 2), y_predict_percent['percent'].max(), y_predict_percent['percent'].min())),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger='axis')
        )
        line2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        return line, scat, line2

    def search_sim_dateList(self, date_base, refer):
        sql = "select 运行日期, 竞价容量比最大, 竞价容量比最小, 竞价容量比平均 from `能源日前均值`"
        df_avg = pd.read_sql(sql, ch.connect).dropna()
        df_avg = df_avg[pd.to_datetime(df_avg['运行日期']) < pd.to_datetime(date_base)]
        df_avg['最大差值'] = df_avg['竞价容量比最大'].map(lambda x: abs(x - refer['竞价容量比最大'].values).round(4))
        df_avg['最小差值'] = df_avg['竞价容量比最小'].map(lambda x: abs(x - refer['竞价容量比最小'].values).round(4))
        df_avg['均值差值'] = df_avg['竞价容量比平均'].map(lambda x: abs(x - refer['竞价容量比平均'].values).round(4))
        df_avg['加权差值'] = df_avg.apply(lambda x: (x['最大差值'] + x['最小差值'] + x['均值差值']).round(4), axis=1)
        df_avg.sort_values(by='加权差值', ascending=True, inplace=True)

        return df_avg['运行日期'].tolist()

    def search_sim_line(self, date_base, refer):
        sql = "select 运行日期, 时间, 竞价容量比, 日前均价 from `总表(无历史数据)`"
        data = pd.read_sql(sql, ch.connect).dropna()

        end_date = (date_base + relativedelta(months=-2)).strftime('%Y-%m-%d')
        refer.index = list(range(0, 96))
        refer_data = {'{}'.format(date_base):refer}
        df_sim = pd.DataFrame(data = refer_data, columns=list(range(0, 95)))
        date_list = data['运行日期'][(pd.to_datetime(data['运行日期']) < pd.to_datetime(date_base)) & (pd.to_datetime(data['运行日期']) >= pd.to_datetime(end_date))].sort_values(ascending=True).unique().tolist()
        for d in date_list:
            t1 = data['竞价容量比'][pd.to_datetime(data['运行日期']) == pd.to_datetime(d)]
            t1.index = list(range(0, 96))
            df_sim.loc[d] = abs(t1-refer)
        df_sim['sum'] = df_sim.apply(lambda x: x.sum(), axis=1)
        df_sim.sort_values(by='sum', ascending=True, inplace=True)

        return df_sim.index.tolist()


if __name__ == '__main__':
    ch = Charts(mysql_setting['host'], mysql_setting['port'], mysql_setting['user'], mysql_setting['password'],
                mysql_setting['database'])
    # price_jjkj = ch.draw_price_jjkj()  # 绘制价格与竞价空间
    # price_jjkj_html = price_jjkj.render_embed()
    st.set_page_config(layout="wide")
    agree = st.sidebar.radio('请选择显示项', ('市场动态', '市场分析'), index=1)
    scdt = st.sidebar.selectbox('市场动态', ['信息看板', '交易结果'], index=1)
    scfx = st.sidebar.selectbox('市场分析', ['现货价格分析', '竞价空间分析', '价格预测'], index=2)
    # events = {'click':'function(params){return params.name}'}

    c21, c22 = st.columns(2)
    c31, c32, c33 = st.columns(3)
    c41, c42, c43, c44 = st.columns(4)
    c91, c92 = st.columns([8, 1])
    if agree == '市场动态':
        if scdt == '信息看板':
            sql = "select * from 总表 where 预测 = 0"
            df_info_board = pd.read_sql(sql, ch.connect)
            df_info_board['运行时间'] = df_info_board['运行日期'].map(str) + ' ' + df_info_board['时间'].map(str)
            begin_date = c21.selectbox('开始日期', df_info_board['运行日期'].sort_values(ascending=False).unique().tolist(),
                                       index=0)
            end_date = c22.selectbox('结束日期', df_info_board['运行日期'][
                pd.to_datetime(df_info_board['运行日期']) >= pd.to_datetime(begin_date)].sort_values(
                ascending=False).unique().tolist(), index=0)
            df_info = df_info_board[(pd.to_datetime(df_info_board['运行日期']) >= pd.to_datetime(begin_date)) & (
                    pd.to_datetime(df_info_board['运行日期']) <= pd.to_datetime(end_date))]
            e_energy, e_market_price = ch.draw_info_board(df_info)  # 绘制日前市场供需情况
            st_pyecharts(e_energy, theme=ThemeType.WALDEN, height='500px')
            st_pyecharts(e_market_price, theme=ThemeType.WALDEN, height='500px')

        elif scdt == '交易结果':
            sql = "select * from 滚动交易"
            df_trade_result = pd.read_sql(sql, ch.connect)
            trade_date = c21.selectbox('交易日', df_trade_result['交易日'].sort_values(ascending=False).unique().tolist(),
                                       index=0)
            run_date = c22.selectbox('运行日',
                                     df_trade_result['运行日'][df_trade_result['交易日'] == trade_date].unique().tolist(),
                                     index=0)
            df_trade = df_trade_result[(df_trade_result['交易日'] == trade_date) & (df_trade_result['运行日'] == run_date)]
            e_trade_result = ch.draw_trade_result(df_trade)
            # c92.metric(label='总交易电量', value='{}MWh'.format(df_trade['交易电量(日均)'].sum().round(3)))
            # with c91:
            st_pyecharts(e_trade_result, theme=ThemeType.PURPLE_PASSION, height='500px')

            c_31, c_32, c_33 = st.columns([1, 2, 7])
            c_1, c_2, c_3, c_4, c_5 = st.columns(5)
            mode = c_31.radio('请选择模式', ('交易日-运行日', '运行日'), index=1)
            if mode == '运行日':
                exec_date = c_32.selectbox('运行日期',
                                           df_trade_result['运行日'].sort_values(ascending=False).unique().tolist(),
                                           index=24)
                df_profit = df_trade_result[df_trade_result['运行日'] == exec_date]
                e_profit = ch.draw_profit_result(df_profit, '运行日')
            elif mode == '交易日-运行日':
                df_profit = df_trade
                e_profit = ch.draw_profit_result(df_profit, '交易日-运行日')

            st_pyecharts(e_profit, theme=ThemeType.WALDEN, height='500px')
            # c_2.metric(label='总盈亏', value='{}万元'.format(df_profit['总盈亏(万元)'].sum().round(3)))
            # c_3.metric(label='偏差处理盈亏',
            #             value='{}元'.format(df_profit['偏差处理/主动套利盈亏'][df_profit['盈亏类型'] == 0].sum().round(3)))
            # c_4.metric(label='主动套利盈亏',
            #             value='{}元'.format(df_profit['偏差处理/主动套利盈亏'][df_profit['盈亏类型'] == 1].sum().round(3)))

    elif agree == '市场分析':
        if scfx == '现货价格分析':
            tab1, tab2, tab3 = st.tabs(['📈日前或实时价格', '📈日前实时价格对比', '📈价格与竞价空间趋势'])
            sql = "select * from 总表 where 预测 = 0"
            df_info_price = pd.read_sql(sql, ch.connect)

            with tab1:
                t1_cc51, t1_cc52, t1_cc53, t1_cc54, t1_cc55 = tab1.columns([1, 1, 2, 2, 1])
                t1_cc21, t1_cc22 = tab1.columns([5, 1])

                is_real = t1_cc51.selectbox('日前&实时', ['日前价格', '实时价格'])
                is_compress = t1_cc52.selectbox('价格压缩', ['压缩', '不压缩'], key='tab1_compress')
                begin_date = t1_cc53.selectbox('开始日期',
                                               df_info_price['运行日期'].sort_values(ascending=False).unique().tolist(),
                                               index=0, key='tab1_begin_date')
                end_date = t1_cc54.selectbox('结束日期', df_info_price['运行日期'][
                    pd.to_datetime(df_info_price['运行日期']) >= pd.to_datetime(begin_date)].sort_values(
                    ascending=False).unique().tolist(), index=0, key='tab1_end_date')
                df_price = df_info_price[(pd.to_datetime(df_info_price['运行日期']) >= pd.to_datetime(begin_date)) & (
                        pd.to_datetime(df_info_price['运行日期']) <= pd.to_datetime(end_date))]

                if (is_real == '日前价格') & (is_compress == '压缩'):
                    e_price = ch.draw_price(df_price, False, True, begin_date, end_date)
                    avg = df_price.groupby('小时')['日前价格(压缩)'].mean()
                elif (is_real == '日前价格') & (is_compress == '不压缩'):
                    e_price = ch.draw_price(df_price, False, False, begin_date, end_date)
                    avg = df_price.groupby('小时')['日前价格'].mean()
                elif (is_real == '实时价格') & (is_compress == '压缩'):
                    e_price = ch.draw_price(df_price, True, True, begin_date, end_date)
                    avg = df_price.groupby('小时')['实时价格(压缩)'].mean()
                elif (is_real == '实时价格') & (is_compress == '不压缩'):
                    e_price = ch.draw_price(df_price, True, False, begin_date, end_date)
                    avg = df_price.groupby('小时')['实时价格'].mean()

                with t1_cc21:
                    st_pyecharts(e_price, theme=ThemeType.WALDEN, height='600px')
                with t1_cc22:
                    avg.name = '均价'
                    avg = avg.round(2)
                    st.write(avg)
                    st.metric(label='均价', value="%.2f" % avg.mean())

            with tab2:
                t2_cc41, t2_cc42, t2_cc43, t2_cc44 = tab2.columns([1, 2, 2, 2])
                t2_cc21, t2_cc22 = tab2.columns([5, 1])
                is_compress = t2_cc41.selectbox('价格压缩', ['压缩', '不压缩'], key='tab2_compress')
                begin_date = t2_cc42.selectbox('开始日期',
                                               df_info_price['运行日期'].sort_values(ascending=False).unique().tolist(),
                                               index=0, key='tab2_begin_date')
                end_date = t2_cc43.selectbox('结束日期', df_info_price['运行日期'][
                    pd.to_datetime(df_info_price['运行日期']) >= pd.to_datetime(begin_date)].sort_values(
                    ascending=False).unique().tolist(), index=0, key='tab2_end_date')
                df_price = df_info_price[(pd.to_datetime(df_info_price['运行日期']) >= pd.to_datetime(begin_date)) & (
                        pd.to_datetime(df_info_price['运行日期']) <= pd.to_datetime(end_date))]

                if is_compress == '压缩':
                    e_date, e_time = ch.draw_price_compare(df_price, True, begin_date, end_date)
                else:
                    e_date, e_time = ch.draw_price_compare(df_price, False, begin_date, end_date)

                with t2_cc21:
                    st_pyecharts(e_date, theme=ThemeType.WALDEN, height='500px')
                    st_pyecharts(e_time, theme=ThemeType.WALDEN, height='500px')
            with tab3:
                t3_cc41, t3_cc42, t3_cc43, t3_cc44 = tab3.columns([1, 2, 2, 2])
                t3_cc21, t3_cc22 = tab3.columns([5, 1])
                is_compress = t3_cc41.selectbox('价格压缩', ['压缩', '不压缩'], key='tab3_compress')
                begin_date = t3_cc42.selectbox('开始日期',
                                               df_info_price['运行日期'].sort_values(ascending=False).unique().tolist(),
                                               index=0, key='tab3_begin_date')
                end_date = t3_cc43.selectbox('结束日期', df_info_price['运行日期'][
                    pd.to_datetime(df_info_price['运行日期']) >= pd.to_datetime(begin_date)].sort_values(
                    ascending=False).unique().tolist(), index=0, key='tab3_end_date')
                df_compete = df_info_price[(pd.to_datetime(df_info_price['运行日期']) >= pd.to_datetime(begin_date)) & (
                        pd.to_datetime(df_info_price['运行日期']) <= pd.to_datetime(end_date))]
                e_compete = ch.draw_price_jjkj(df_compete, is_compress)
                st_pyecharts(e_compete, theme=ThemeType.WALDEN, height='500px')
        elif scfx == '竞价空间分析':
            tab1, tab2 = st.tabs(['供给曲线拟合-竞价空间', '竞价空间分析'])
            sql = "select * from 总表 where 预测 = 0"
            df_info_compete = pd.read_sql(sql, ch.connect)

            with tab1:
                c21, c22 = st.columns(2)
                mode = c21.radio('请选择模式', ('开始日期-结束日期', '日期'), index=0)
                c21, c22 = st.columns(2)
                if mode == '开始日期-结束日期':
                    begin_date = c21.selectbox('开始日期',
                                               df_info_compete['运行日期'].sort_values(ascending=False).unique().tolist(),
                                               index=0)
                    end_date = c22.selectbox('结束日期', df_info_compete['运行日期'][
                        pd.to_datetime(df_info_compete['运行日期']) >= pd.to_datetime(begin_date)].sort_values(
                        ascending=False).unique().tolist(), index=0)
                    df_compete = df_info_compete[
                        (pd.to_datetime(df_info_compete['运行日期']) >= pd.to_datetime(begin_date)) & (
                                pd.to_datetime(df_info_compete['运行日期']) <= pd.to_datetime(end_date))]
                    datelist = pd.date_range(begin_date, end_date, freq='D').strftime("%Y-%m-%d").to_list()
                elif mode == '日期':
                    datelist = st.multiselect('请选择日期',
                                              df_info_compete['运行日期'].sort_values(ascending=False).unique().astype(
                                                  str).tolist(),
                                              df_info_compete['运行日期'].sort_values(ascending=False).unique().astype(
                                                  str).tolist()[0])
                    df_compete = pd.DataFrame(columns=df_info_compete.columns.to_list())
                    for date in datelist:
                        df = df_info_compete[pd.to_datetime(df_info_compete['运行日期']) == pd.to_datetime(date)]
                        df_compete = pd.concat([df_compete, df], axis=0)

                e_compete, e_compete_percent, e_compete_3d = ch.draw_jjkj_curve(df_compete, datelist)
                st_pyecharts(e_compete, theme=ThemeType.WALDEN, height='600px')
                st_pyecharts(e_compete_percent, theme=ThemeType.WALDEN, height='600px')
                st_pyecharts(e_compete_3d, theme=ThemeType.WALDEN, height='700px')

        elif scfx == '价格预测':
            #######################################################################################################################
            st.header('价格复盘')
            c41, c42, c43, c44 = st.columns(4)
            sql1 = 'select 运行日期, 预测日期, 预测, 时间, 小时, 竞价容量比, 日前价格 from 总表'
            df_sim = pd.read_sql(sql1, ch.connect)
            sim_match_date = c41.selectbox('运行日', df_sim['预测日期'].sort_values(ascending=False).unique().tolist(),index=0)
            sim_predict_dateList = c42.multiselect('预测日', df_sim['预测日期'][(pd.to_datetime(df_sim['运行日期']) == pd.to_datetime(sim_match_date)) & (df_sim['预测'] != 0)].sort_values(ascending=False).unique().tolist(), df_sim['预测日期'][(pd.to_datetime(df_sim['运行日期']) == pd.to_datetime(sim_match_date)) & (df_sim['预测'] != 0)].sort_values(ascending=False).unique().tolist()[0])
            mode = c43.radio('模式', ('相似日', '日期范围'), index=0)
            sim_order = c44.selectbox('曲线阶数', list(range(1, 41)))

            df_match_date = df_sim[['竞价容量比', '日前价格']][(pd.to_datetime(df_sim['预测日期']) == pd.to_datetime(sim_match_date)) & (df_sim['预测']==0)]
            df_match_date.columns = ['{}竞价容量比'.format(sim_match_date), '{}日前价格'.format(sim_match_date)]
            for p in sim_predict_dateList:
                df_predict_percent = df_sim['竞价容量比'][(pd.to_datetime(df_sim['运行日期']) == pd.to_datetime(sim_match_date)) & (pd.to_datetime(df_sim['预测日期']) == pd.to_datetime(p))]
                df_predict_percent.name = '{}->{}竞价容量比'.format(p, sim_match_date)
                c31, c32, c33 = st.columns(3)
                if mode == '相似日':
                    # refer_data = {'竞价容量比最大':[df_predict_percent.max()],
                    #          '竞价容量比最小':[df_predict_percent.min()],
                    #          '竞价容量比平均':[df_predict_percent.mean()]}
                    # refer = pd.DataFrame(refer_data)
                    # dateList = ch.search_sim_dateList(p, refer)
                    dateList = ch.search_sim_line(p, df_predict_percent)
                    sim_predict_dateList = c31.multiselect('{}->{}相似日'.format(p, sim_match_date), dateList, dateList[0])
                    df_refer = df_sim[['竞价容量比', '日前价格']][(pd.to_datetime(df_sim['预测日期']) == pd.to_datetime(p)) & (df_sim['预测']==0)]
                    df_refer.columns=['{}竞价容量比'.format(p), '{}日前价格'.format(p)]
                    df_refer.index = list(range(0, 96))
                    for i in sim_predict_dateList:
                        df_i = df_sim[['竞价容量比', '日前价格']][(pd.to_datetime(df_sim['预测日期']) == pd.to_datetime(i)) & (df_sim['预测']==0)]
                        df_i.columns=['{}竞价容量比'.format(i), '{}日前价格'.format(i)]
                        df_i.index = list(range(0, 96))
                        df_refer = pd.concat([df_refer, df_i], axis=1)
                    e_simLine, e_simScat, e_simPredict = ch.draw_price_similar(df_match_date, df_predict_percent, df_refer, sim_order)
                    c31, c32, c33 = st.columns(3)
                    with c31:
                        st_pyecharts(e_simLine, theme=ThemeType.WALDEN, height='600px')
                    with c32:
                        st_pyecharts(e_simScat, theme=ThemeType.WALDEN, height='600px')
                    with c33:
                        st_pyecharts(e_simPredict, theme=ThemeType.WALDEN, height='600px')
                elif mode == '日期范围':
                    a = 1

                # sim_date = c41.multiselect('未来{}天相似日'.format(i),)
                # sim_order = c42.select('预测阶数', list(range(2, 41)), index = 0)
            # df_sim_exec = df_sim['竞价容量比'][(pd.to_datetime(df_sim['运行日期']) == pd.to_datetime(sim_match_date)) & (df_info_price['预测'] == 1)]
            # df_sim_exec.name = '{}昨日预测竞价容量比'.format(sim_match_date)
            # df_sim_actual = df_sim
            # c31, c32, c33 = st.columns(3)
            # with c31:

            # sql1 = "select 运行日期, 竞价容量比最大, 竞价容量比最小, 竞价容量比平均 from `能源日前均值`"
            # df_avg = pd.read_sql(sql1, ch.connect).dropna()
            # sql2 = 'select 运行日期, 时间, 小时, 竞价容量比, 日前价格 from `总表(无历史数据)`'
            # # sql2 = "select 运行日期, 预测时间, 预测, 时间, 小时, 竞价容量比, 日前价格 from 总表 where 预测 = 0"
            # df_sim = pd.read_sql(sql2, ch.connect).dropna()
            # refer = df_avg[['竞价容量比最大','竞价容量比最小', '竞价容量比平均']][pd.to_datetime(df_avg['运行日期']) == pd.to_datetime(sim_match_date)]
            # df_avg = df_avg[pd.to_datetime(df_avg['运行日期']) <= pd.to_datetime(sim_match_date)]
            # df_avg['最大差值'] = df_avg['竞价容量比最大'].map(lambda x: abs(x - refer['竞价容量比最大'].values).round(4))
            # df_avg['最小差值']=df_avg['竞价容量比最小'].map(lambda x: abs(x - refer['竞价容量比最小'].values).round(4))
            # df_avg['均值差值']=df_avg['竞价容量比平均'].map(lambda x: abs(x - refer['竞价容量比平均'].values).round(4))
            # df_avg['加权差值']=df_avg.apply(lambda x: (x['最大差值'] +  x['最小差值'] +  x['均值差值']).round(4), axis=1)
            # df_avg.sort_values(by='加权差值', ascending=True,inplace=True)
            # sim_dateList = c42.multiselect('相似日', df_avg['运行日期'].tolist(), df_avg['运行日期'].tolist()[0])
            # # sim_refer_date = c42.select('参照日', df_info_price['预测日期'][(pd.to_datetime(df_info_price['运行日期']) == pd.to_datetime(sim_match_date)) & (df_info_price['预测'] != 0)].sort_values(ascending=False).unique().tolist(), index = 0)
            # sim_MonthList = c43.multiselect('同期相似日', df_avg['运行日期'][pd.to_datetime(df_avg['运行日期']).dt.month == sim_match_date.month].tolist(), df_avg['运行日期'][pd.to_datetime(df_avg['运行日期']).dt.month == sim_match_date.month].tolist()[0])
            # # sim_MonthList = c43.multiselect('参照日-同期相似日', df_avg['运行日期'][pd.to_datetime(df_avg['运行日期']).dt.month == sim_refer_date.month].tolist(), df_avg['运行日期'][pd.to_datetime(df_avg['运行日期']).dt.month == sim_refer_date.month].tolist()[0])
            # sim_order = c44.selectbox('阶数', list(range(1, 41)), index=0)
            # c21, c22 = st.columns(2)
            # e_sim = ch.draw_price_similar(df_sim, sim_MonthList)
            # with c21:
            #     st_pyecharts(e_sim, theme=ThemeType.WALDEN, height='600px')
            # st.write(refer)
            # st.write(df_avg)
            #######################################################################################################################
            st.header('预测价格')
            c41, c42, c43, c44 = st.columns(4)
            sql1 = 'select 运行日期, 预测日期, 预测, 时间, 小时, 竞价容量比, 日前价格 from 总表'
            df_pre = pd.read_sql(sql1, ch.connect)
            predict_date = c41.selectbox('预测日期', df_pre['预测日期'].sort_values(ascending=False).unique().tolist(),index=0)
            exec_dateList = df_pre['运行日期'][pd.to_datetime(df_pre['预测日期']) == pd.to_datetime(predict_date)].sort_values().unique().tolist()
            if len(exec_dateList) != 1:
                exec_dateList.pop(0)
                for i in range(len(exec_dateList)):
                    if i >= 3:
                        break
                    exec_date = exec_dateList[i]
                    predict_percent = df_pre['竞价容量比'][(pd.to_datetime(df_pre['预测日期']) == pd.to_datetime(predict_date)) & (pd.to_datetime(df_pre['运行日期']) == pd.to_datetime(exec_date))]
                    sim_dateList = ch.search_sim_line(exec_date, predict_percent)
                    c41, c42, c43, c44 = st.columns(4)
                    sim_dateList = c41.multiselect('{}->{}相似日'.format(predict_date, exec_date), sim_dateList, sim_dateList[0])
                    df_sim = pd.DataFrame(data = predict_percent.apply(lambda x: x * 100).round(2), index=range(0, 96))
                    for s in sim_dateList:
                        df_temp = df_pre[['竞价容量比', '日前价格']][(pd.to_datetime(df_pre['预测日期']) == pd.to_datetime(s)) & (df_pre['预测'] == 0)]
                        df_temp['竞价容量比'] = df_temp['竞价容量比'].apply(lambda x: x * 100).round(2)
                        df_temp.columns = ['{}竞价容量比'.format(s), '{}日前价格'.format(s)]
                        df_temp.index = range(0, 96)
                        df_sim = pd.concat([df_sim, df_temp], axis=1)
                    df_predict = df_pre[['竞价容量比', '日前价格']][(pd.to_datetime(df_pre['预测日期']) == pd.to_datetime(predict_date)) & (df_pre['预测'] == 0)]
                    df_predict['竞价容量比'] = df_predict['竞价容量比'].apply(lambda x: x * 100).round(2)
                    df_predict.columns = ['{}竞价容量比'.format(predict_date), '{}日前价格'.format(predict_date)]
                    df_predict.index = range(0, 96)
                    e_line, e_scat, e_line2 = ch.draw_price_predict(df_sim, df_predict)
                    c31, c32, c33 = st.columns(3)
                    with c31:
                        st_pyecharts(e_line, theme=ThemeType.WALDEN, height='400px')
                    with c32:
                        st_pyecharts(e_scat, theme=ThemeType.WALDEN, height='400px')
                    with c33:
                        st_pyecharts(e_line2, theme=ThemeType.WALDEN, height='400px')
            #######################################################################################################################
            # c21, c22 = st.columns(2)
            # sql = "select 运行日期, 预测日期, 时间, 小时, 竞价容量比, 竞价空间, `日前价格`, 预测 from 总表 where 竞价容量比 is not NULL"
            # df_info_price = pd.read_sql(sql, ch.connect)
            #
            # date = c21.selectbox('请选择日期', df_info_price['预测日期'].sort_values(ascending=False).unique().tolist(), index=0)
            # # date = pd.datetime.strptime('2023-06-08', '%Y-%m-%d')
            # is_doc = c22.radio('是否使用本地记录', ('是', '否'), index=0)
            # df_price = df_info_price[['竞价容量比', '日前价格']][
            #     (pd.to_datetime(df_info_price['预测日期']) == pd.to_datetime(date)) & (df_info_price['预测'] == 0)]
            # df_price.columns = ['{}_竞价容量比'.format(date), '{}_日前价格'.format(date)]
            # df_price.sort_values(by='{}_竞价容量比'.format(date), inplace=True)
            # exec_dateList = df_info_price['运行日期'][
            #     pd.to_datetime(df_info_price['预测日期']) == pd.to_datetime(date)].unique().tolist()
            # for i in range(1, len(exec_dateList)):
            #     if i > 3:
            #         break
            #     df_price.insert(loc=i * 2, column='{}_竞价容量比'.format(exec_dateList[i]), value=df_info_price['竞价容量比'][
            #         (pd.to_datetime(df_info_price['运行日期']) == pd.to_datetime(exec_dateList[i])) & (
            #                 df_info_price['预测'] == i)].tolist())
            #     df_price['{}_日前价格'.format(exec_dateList[i])] = ""
            # df_price.index = list(range(0, 96))
            # for i in range(2, df_price.shape[1], 2):
            #     for j in range(0, 96):
            #         find_data = df_price.iloc[j, i]
            #         reference_df = df_price.iloc[:, 0]
            #         df_price.iloc[j, i + 1] = df_price.iloc[
            #             (reference_df - find_data).abs().sort_values().index[0], 1]
            #
            # if is_doc == '否':
            #     df_ref = df_price
            # elif is_doc == '是':
            #     file = file_setting['predict']
            #     is_exists = os.path.exists(file)
            #     sheet = date.strftime('%Y-%m-%d')
            #     if (is_exists) and (sheet in pd.ExcelFile(file).sheet_names):
            #         db = pd.read_excel(file, sheet_name=sheet)
            #         df_ref = db
            #     else:
            #         if not is_exists:
            #             wb = openpyxl.Workbook()
            #             wb.save(file)
            #         df_ref = df_price
            #         writer = pd.ExcelWriter(file, mode="a", engine="openpyxl", if_sheet_exists="replace")
            #         pd.DataFrame(df_ref).to_excel(writer, sheet_name=sheet, index=False)
            #         writer.save()
            #
            # e_scat, e_price = ch.draw_profit_price(df_ref)
            # with c21:
            #     st_pyecharts(e_scat, theme=ThemeType.WALDEN, height='600px')
            # with c22:
            #     st_pyecharts(e_price, theme=ThemeType.WALDEN, height='600px')
            #######################################################################################################################
            # # dic = {'竞价空间': df_info_price['竞价空间'][
            # #     (pd.to_datetime(df_info_price['预测日期']) == pd.to_datetime(date)) & (df_info_price['预测'] == 0)],
            # #        '竞价容量比': df_info_price['竞价容量比'][
            # #            (pd.to_datetime(df_info_price['预测日期']) == pd.to_datetime(date)) & (df_info_price['预测'] == 0)],
            # #        '日前价格': df_info_price['日前价格'][
            # #            (pd.to_datetime(df_info_price['预测日期']) == pd.to_datetime(date)) & (df_info_price['预测'] == 0)],
            # #        '运行日期': [date.strftime('%Y-%m-%d')] * 96}
            # # df_price_modify = pd.DataFrame(dic)
            # # df_price_modify.index = list(range(0, 96))
            # # datelist = [date]
            # # e_compete, e_compete_percent, e_compete_3d = ch.draw_jjkj_curve(df_price_modify, datelist)
            # # st_pyecharts(e_compete_percent, theme=ThemeType.WALDEN, height='600px')
            # c41, c42, c43, c44 = st.columns(4)
            # match_date = c41.selectbox('拟合日期', df_info_price['预测日期'].sort_values(ascending=False).unique().tolist(),
            #                            index=0)
            # refer_dateList = c42.multiselect('参考日期', df_info_price['预测日期'][
            #     (pd.to_datetime(df_info_price['运行日期']) == pd.to_datetime(match_date)) & (
            #             df_info_price['预测'] != 0)].sort_values(ascending=False).unique().tolist(),
            #                                  df_info_price['预测日期'][(pd.to_datetime(
            #                                      df_info_price['运行日期']) == pd.to_datetime(match_date)) & (
            #                                                                df_info_price['预测'] != 0)].sort_values(
            #                                      ascending=False).unique().tolist()[0])
            # order = c43.selectbox('拟合阶数', list(range(1, 41)), index=2)
            # df_price_modify = df_info_price[['竞价容量比', '日前价格']][
            #     (pd.to_datetime(df_info_price['预测日期']) == pd.to_datetime(match_date)) & (df_info_price['预测'] == 0)]
            # df_price_modify.columns = ['{}_竞价容量比'.format(match_date), '{}_日前价格'.format(match_date)]
            # df_price_modify.iloc[:, 0] = df_price_modify.iloc[:, 0].apply(lambda x: x * 100).round(2)
            # df_price_modify.index = list(range(0, 96))
            # for d in refer_dateList:
            #     df_temp = df_info_price[['竞价容量比', '日前价格']][
            #         (pd.to_datetime(df_info_price['运行日期']) == pd.to_datetime(d)) & (df_info_price['预测'] == 0)]
            #     df_temp.iloc[:, 0] = df_temp.iloc[:, 0].apply(lambda x: x * 100).round(2)
            #     df_temp.columns = ['{}_竞价容量比'.format(d), '{}_日前价格'.format(d)]
            #     df_temp.index = list(range(0, 96))
            #     df_price_modify = pd.concat([df_price_modify, df_temp], axis=1)
            #
            #     df_temp = df_info_price[['竞价容量比']][
            #         (pd.to_datetime(df_info_price['运行日期']) == pd.to_datetime(match_date)) & (
            #                 pd.to_datetime(df_info_price['预测日期']) == pd.to_datetime(d))]
            #     df_temp.iloc[:, 0] = df_temp.iloc[:, 0].apply(lambda x: x * 100).round(2)
            #     df_temp.columns = ['{}'.format(d)]
            #     df_temp.index = list(range(0, 96))
            #     df_price_modify = pd.concat([df_price_modify, df_temp], axis=1)
            #
            # c21, c22 = st.columns(2)
            # e_modify, e_predict = ch.draw_modify_price(df_price_modify, refer_dateList, order)
            # with c21:
            #     st_pyecharts(e_modify, theme=ThemeType.WALDEN, height='600px')
            # with c22:
            #     st_pyecharts(e_predict, theme=ThemeType.WALDEN, height='600px')
            #
            # #######################################################################################################################
            # c21, c22 = st.columns(2)
            # exec_date = c21.selectbox('运行日期', df_info_price['预测日期'].sort_values(ascending=False).unique().tolist(),
            #                           index=0)
            # predict_date = c22.multiselect('预测日期', df_info_price['预测日期'][
            #     pd.to_datetime(df_info_price['运行日期']) == pd.to_datetime(exec_date)].sort_values(
            #     ascending=False).unique().tolist(), df_info_price['预测日期'][
            #                                    pd.to_datetime(df_info_price['运行日期']) == pd.to_datetime(
            #                                        exec_date)].sort_values(ascending=False).unique().tolist()[0])
            # df_value = pd.DataFrame(data=df_info_price['竞价容量比'][
            #     (pd.to_datetime(df_info_price['运行日期']) == pd.to_datetime(exec_date)) & (
            #             df_info_price['预测'] == 0)].tolist(),
            #                         columns=['{}_竞价容量比'.format(exec_date)], index=list(range(0, 96)))
            # col = 1
            # for i in predict_date:
            #     if i == exec_date:
            #         df_value.insert(loc=col, column='{}_日前价格'.format(i), value=df_info_price['日前价格'][
            #             (pd.to_datetime(df_info_price['预测日期']) == pd.to_datetime(exec_date)) & (
            #                     df_info_price['预测'] == 0)].tolist())
            #         col += 1
            #     else:
            #         df_refer = df_info_price[['竞价容量比', '日前价格']][
            #             (pd.to_datetime(df_info_price['预测日期']) == pd.to_datetime(i)) & (df_info_price['预测'] == 0)]
            #         df_refer.columns = ['{}_竞价容量比'.format(i), '{}_日前价格'.format(i)]
            #         df_refer.insert(loc=2, column='{}_竞价容量比'.format(exec_date), value=df_info_price['竞价容量比'][
            #             (pd.to_datetime(df_info_price['运行日期']) == pd.to_datetime(exec_date)) & (
            #                     pd.to_datetime(df_info_price['预测日期']) == pd.to_datetime(i))].tolist())
            #         df_refer['{}_日前价格'.format(exec_date)] = ""
            #         df_refer.index = list(range(0, 96))
            #         for j in range(0, 96):
            #             find_data = df_refer.iloc[j, 2]
            #             reference_df = df_refer.iloc[:, 0]
            #             df_refer.iloc[j, 3] = df_refer.iloc[(reference_df - find_data).abs().sort_values().index[0], 1]
            #
            #         df_value.insert(loc=col, column='{}_预测日前价格'.format(i), value=df_refer.iloc[:, 3])
            # df_value.drop(labels='{}_竞价容量比'.format(exec_date), axis=1, inplace=True)
            # e_reverse = ch.draw_reverse(df_value)
            # st_pyecharts(e_reverse, theme=ThemeType.WALDEN, height='600px')

            # page = Page()
            # page.add(energy, market_price)
            # page.render('折线图.html')
