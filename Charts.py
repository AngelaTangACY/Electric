from pyecharts.charts import Line, Page, Grid, Bar, Scatter, Scatter3D
import pyecharts.options as opts
from pyecharts.faker import Faker
from  pyecharts.charts import *
from pyecharts.globals import ThemeType, RenderType
import pymysql
import pandas as pd
from streamlit_echarts import st_pyecharts
import streamlit as st
import datetime
import streamlit.components.v1 as components
from pyecharts.commons.utils import JsCode

mysql_setting = {
    'host': "localhost",
    'port': 3306,
    'user': "root",
    'password': '123456',
    'database': 'data',
    'charset': 'utf8'
}


def connect(host, port, user, password, database):
    connect = pymysql.connect(host=host,
                              port=port,
                              user=user,
                              password=password,
                              database=database,
                              charset='utf8')
    cursor = connect.cursor()
    return connect


# 绘制日前市场供需情况:省内负荷、外送、新能源、竞价空间图
# 绘制市场价格趋势(实时价格、日前价格)
def draw_info_board(df_info):
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
def draw_trade_result(trade_df):
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
    line.add_yaxis('最低价', y_axis=trade_df['最低价'].tolist(), symbol_size=1, linestyle_opts=opts.LineStyleOpts(width=2))
    line.add_yaxis('日前价格(压缩平均)', y_axis=trade_df['日前价格(压缩平均)'].tolist(), symbol_size=1,
                   linestyle_opts=opts.LineStyleOpts(width=2, type_='dashed'))
    line.add_yaxis('成交均价',
                   y_axis=trade_df['交易电价'].tolist(),
                   symbol='triangle',
                   symbol_size=15,
                   linestyle_opts=opts.LineStyleOpts(is_show=False),
                   itemstyle_opts=opts.ItemStyleOpts(color='black')
                   )
    line.add_yaxis('加权价', y_axis=trade_df['加权价格'].tolist(), symbol_size=1, linestyle_opts=opts.LineStyleOpts(width=2))
    line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

    bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
    bar.add_xaxis(trade_df['时段'].tolist())
    bar.add_yaxis('总交易量(日均)', y_axis=trade_df['总交易量(日均)'].tolist(), z=0)
    bar.add_yaxis('交易电量(日均)+', y_axis=trade_df_rep['交易电量(日均)'][trade_df_rep['交易电量(日均)'] >= 0].tolist(), z=0,
                  itemstyle_opts=opts.ItemStyleOpts(color='green'))
    bar.add_yaxis('交易电量(日均)-', y_axis=trade_df_rep['交易电量(日均)'][trade_df_rep['交易电量(日均)'] <= 0].tolist(), z=0,
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
                                                  subtitle='总交易电量:' + str(df_trade['交易电量(日均)'].sum().round(3)) + 'MWh',
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


def draw_profit_result(profit_df, mode):
    profit_df.fillna(0, inplace=True)
    if mode == '运行日':
        bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        bar.add_xaxis(profit_df['小时'].unique().tolist())
        df = profit_df.groupby('小时').sum()[['偏差处理/主动套利盈亏', '盈亏类型']]
        bar.add_yaxis('偏差处理盈亏+', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] != 0) | (df['偏差处理/主动套利盈亏'] < 0), 0).tolist(),
                      itemstyle_opts=opts.ItemStyleOpts(color='blue'))
        bar.add_yaxis('偏差处理盈亏-', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] != 0) | (df['偏差处理/主动套利盈亏'] > 0), 0).tolist(),
                      itemstyle_opts=opts.ItemStyleOpts(color='red'))
        bar.add_yaxis('主动套利盈亏+', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] == 0) | (df['偏差处理/主动套利盈亏'] < 0), 0).tolist(),
                      itemstyle_opts=opts.ItemStyleOpts(color='green'))
        bar.add_yaxis('主动套利盈亏-', df['偏差处理/主动套利盈亏'].mask((df['盈亏类型'] == 0) | (df['偏差处理/主动套利盈亏'] > 0), 0).tolist(),
                      itemstyle_opts=opts.ItemStyleOpts(color='pink'))
        bar.set_global_opts(legend_opts=opts.LegendOpts(type_="scroll", pos_right="0", pos_top='5%', orient="vertical"),
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
        bar.add_yaxis('偏差处理盈亏+',
                      profit_df['偏差处理/主动套利盈亏'][(profit_df['盈亏类型'] == 0) & (profit_df['偏差处理/主动套利盈亏'] >= 0)].tolist(),
                      itemstyle_opts=opts.ItemStyleOpts(color='blue'))
        bar.add_yaxis('偏差处理盈亏-',
                      profit_df['偏差处理/主动套利盈亏'][(profit_df['盈亏类型'] == 0) & (profit_df['偏差处理/主动套利盈亏'] <= 0)].tolist(),
                      itemstyle_opts=opts.ItemStyleOpts(color='red'))
        bar.add_yaxis('主动套利盈亏+', profit_df['偏差处理/主动套利盈亏'][(profit_df['盈亏类型'] == 1) & (profit_df['偏差处理/主动套利盈亏'] >= 0)],
                      itemstyle_opts=opts.ItemStyleOpts(color='green'))
        bar.add_yaxis('主动套利盈亏-', profit_df['偏差处理/主动套利盈亏'][(profit_df['盈亏类型'] == 1) & (profit_df['偏差处理/主动套利盈亏'] <= 0)],
                      itemstyle_opts=opts.ItemStyleOpts(color='pink'))
        bar.set_global_opts(legend_opts=opts.LegendOpts(type_="scroll", pos_right="0", pos_top='5%', orient="vertical"),
                            title_opts=opts.TitleOpts(title_textstyle_opts=opts.TextStyleOpts(font_size=23),
                                                      pos_left='center',
                                                      title='盈亏结果(交易日:' + str(profit_df.iloc[0].交易日) + '---运行日:' + str(
                                                          profit_df.iloc[0].运行日) + ')', subtitle='总盈亏:' + str(
                                    profit_df['总盈亏(万元)'].sum().round(3)) + '万元    '
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
def draw_price(df_price, is_real, is_compress, begin_date, end_date):
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
def draw_price_compare(df_price, is_compress, begin_date, end_date):
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
def draw_price_jjkj(df_compete, is_compress):
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


def draw_jjkj_curve(df_compete, date_list):
    scat1 = Scatter(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
    for date in date_list:
        scat1.add_xaxis(
            df_compete['竞价空间'][pd.to_datetime(df_compete['运行日期']) == pd.to_datetime(date)].unique().tolist())
        scat1.add_yaxis(date,
                        y_axis=df_compete['日前价格'][pd.to_datetime(df_compete['运行日期']) == pd.to_datetime(date)].tolist(),
                        symbol_size=10, label_opts=opts.LabelOpts(is_show=False))
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
        scat2.add_yaxis(date,
                        y_axis=df_compete['日前价格'][pd.to_datetime(df_compete['运行日期']) == pd.to_datetime(date)].tolist(),
                        symbol_size=10, label_opts=opts.LabelOpts(is_show=False))
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


if __name__ == '__main__':
    conn = connect("192.168.1.3", 3306, "user", '123456','data')
    # price_jjkj = ch.draw_price_jjkj()  # 绘制价格与竞价空间
    # price_jjkj_html = price_jjkj.render_embed()
    st.set_page_config(layout="wide")
    agree = st.sidebar.radio('请选择显示项', ('市场动态', '市场分析'), index=0)
    scdt = st.sidebar.selectbox('市场动态', ['信息看板', '交易结果'], index=1)
    scfx = st.sidebar.selectbox('市场分析', ['现货价格分析', '竞价空间分析'], index=1)
    # events = {'click':'function(params){return params.name}'}

    c21, c22 = st.columns(2)
    c31, c32, c33 = st.columns(3)
    c41, c42, c43, c44 = st.columns(4)
    c91, c92 = st.columns([8, 1])
    if agree == '市场动态':
        if scdt == '信息看板':
            sql = "select * from 总表 where 预测 = 0"
            df_info_board = pd.read_sql(sql, conn)
            df_info_board['运行时间'] = df_info_board['运行日期'].map(str) + ' ' + df_info_board['时间'].map(str)
            begin_date = c21.selectbox('开始日期', df_info_board['运行日期'].sort_values(ascending=False).unique().tolist(),
                                       index=0)
            end_date = c22.selectbox('结束日期', df_info_board['运行日期'][
                pd.to_datetime(df_info_board['运行日期']) >= pd.to_datetime(begin_date)].sort_values(
                ascending=False).unique().tolist(), index=0)
            df_info = df_info_board[(pd.to_datetime(df_info_board['运行日期']) >= pd.to_datetime(begin_date)) & (
                pd.to_datetime(df_info_board['运行日期']) <= pd.to_datetime(end_date))]
            e_energy, e_market_price = draw_info_board(df_info)  # 绘制日前市场供需情况
            st_pyecharts(e_energy, theme=ThemeType.WALDEN, height='500px')
            st_pyecharts(e_market_price, theme=ThemeType.WALDEN, height='500px')

        elif scdt == '交易结果':
            sql = "select * from 滚动交易"
            df_trade_result = pd.read_sql(sql, conn)
            trade_date = c21.selectbox('交易日', df_trade_result['交易日'].sort_values(ascending=False).unique().tolist(),
                                       index=0)
            run_date = c22.selectbox('运行日',
                                     df_trade_result['运行日'][df_trade_result['交易日'] == trade_date].unique().tolist(),
                                     index=0)
            df_trade = df_trade_result[(df_trade_result['交易日'] == trade_date) & (df_trade_result['运行日'] == run_date)]
            e_trade_result = draw_trade_result(df_trade)
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
                e_profit = draw_profit_result(df_profit, '运行日')
            elif mode == '交易日-运行日':
                df_profit = df_trade
                e_profit = draw_profit_result(df_profit, '交易日-运行日')

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
            df_info_price = pd.read_sql(sql, conn)

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
                    e_date, e_time = draw_price_compare(df_price, True, begin_date, end_date)
                else:
                    e_date, e_time = draw_price_compare(df_price, False, begin_date, end_date)

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
                e_compete = draw_price_jjkj(df_compete, is_compress)
                st_pyecharts(e_compete, theme=ThemeType.WALDEN, height='500px')
        elif scfx == '竞价空间分析':
            tab1, tab2 = st.tabs(['供给曲线拟合-竞价空间', '竞价空间分析'])
            sql = "select * from 总表 where 预测 = 0"
            df_info_compete = pd.read_sql(sql, conn)

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

                e_compete, e_compete_percent, e_compete_3d = draw_jjkj_curve(df_compete, datelist)
                st_pyecharts(e_compete, theme=ThemeType.WALDEN, height='600px')
                st_pyecharts(e_compete_percent, theme=ThemeType.WALDEN, height='600px')
                st_pyecharts(e_compete_3d, theme=ThemeType.WALDEN, height='700px')
