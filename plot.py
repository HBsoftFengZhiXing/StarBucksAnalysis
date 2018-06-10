# -*- coding: utf-8 -*-
# __Author__: Sdite
# __Email__ : a122691411@gmail.com

with open('./config/layer/jquery-3.3.1.js', encoding='utf-8') as f:
    jquery = f.read()

with open('./config/qwebchannel.js', encoding='utf-8') as f:
    qwebchannel = f.read()

with open('./config/plotly.js', encoding='utf-8') as f:
    plotly = f.read()

def plot(data, layout, identify=[], score=[], fileName='html/plot.html'):
    # 画图模板字符串
    template = '''<html><head><meta charset="utf-8"/></head><body><script type="text/javascript">{jquery}</script><script type="text/javascript">{qwebchannel}</script><script type="text/javascript">{plotly}</script><script src="../config/layer/layer.js"></script><div id="chartId" style="height: 100%; width: 100%;" class="plotly-graph-div"></div><script type="text/javascript">'''.format(jquery=jquery, qwebchannel=qwebchannel, plotly=plotly) \
               + '''var data = {data},layout = {layout},identify = [{id}, []],scoreArr = [{score}, []];'''.format(data=data, layout=layout, id=identify, score=score) \
               + '''function getValue(){var obj = document.getElementById("score"),i = obj.selectedIndex,score = obj.options[i].value;new QWebChannel(qt.webChannelTransport, function(channel){var interactObj = channel.objects.interactObj;interactObj.JSSendMessage(identify[indexx][index] + " "+ score);scoreArr[indexx][index] = scoreArr[indexx][index] + score + ' ';var scores = scoreArr[indexx][index].substr(0, scoreArr[indexx][index].length-1).split(' '),sum = eval(scores.join('+')),numOfScores = scores.length,avgScore = sum / numOfScores;data[indexx].text[index] =data[indexx].text[index].replace(new RegExp('平均评分: .*?分</br>'), '平均评分: ' + avgScore + '分</br>');data[indexx].text[index] =data[indexx].text[index].replace(new RegExp('评分次数: .*?次'), '评分次数: '+ numOfScores + '次');if (avgScore > 8 && indexx != 1){separateOutScoreMoreThanEight(index);}else if (avgScore <= 8 && indexx != 0){separateOutScoreLessThanEight(index);}set(myPlot);});alert('评分成功!');layer.close(layer.index);}function closeLayer(){layer.close(layer.index);}function separateOutScoreMoreThanEightInit(){for (var i = 0; i < scoreArr[0].length; ++i){var scores = scoreArr[0][i].substr(0, scoreArr[0][i].length-1).split(' '),sum = eval(scores.join('+')),numOfScores = scores.length,avgScore = sum / numOfScores;if (avgScore > 8){scoreArr[1].push(scoreArr[0][i]);identify[1].push(identify[0][i]);scoreArr[0].splice(i, 1);identify[0].splice(i, 1);data[1].lat.push(data[0].lat[i]);data[1].lon.push(data[0].lon[i]);data[1].text.push(data[0].text[i]);data[0].lat.splice(i, 1);data[0].lon.splice(i, 1);data[0].text.splice(i, 1);}}}function separateOutScoreLessThanEight(t){scoreArr[0].push(scoreArr[1][t]),identify[0].push(identify[1][t]),scoreArr[1].splice(t,1),identify[1].splice(t,1),data[0].lat.push(data[1].lat[t]),data[0].lon.push(data[1].lon[t]),data[0].text.push(data[1].text[t]),data[1].lat.splice(t,1),data[1].lon.splice(t,1),data[1].text.splice(t,1)}function separateOutScoreMoreThanEight(t){scoreArr[1].push(scoreArr[0][t]),identify[1].push(identify[0][t]),scoreArr[0].splice(t,1),identify[0].splice(t,1),data[1].lat.push(data[0].lat[t]),data[1].lon.push(data[0].lon[t]),data[1].text.push(data[0].text[t]),data[0].lat.splice(t,1),data[0].lon.splice(t,1),data[0].text.splice(t,1)}function set(t){Plotly.newPlot("chartId",data,layout,{showLink:!1,linkText:"Export to plot.ly"}),"scattermapbox"==data[0].type&&document.getElementById("chartId").on("plotly_click",function(t){var e=t.points[0];if("标记点"!=e.text.substr(0,3)){index1=data[0].text.indexOf(e.text),index2=data[1].text.indexOf(e.text),indexx=(index=-1==index1?index2:index1)==index1?0:1;var a=e.text.replace(new RegExp("</br></br>","gm"),"</br>");a+="</br></br>评分: ",layer.open({type:1,title:"店铺评分",maxmin:!1,closeBtn:1,area:["500px","350px"],content:'<div style="display: flex;flex-direction: column;margin: 0 5%;"><p>'+a+'</p><select id="score" name="rating"><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="7">7</option><option value="8">8</option><option value="9">9</option><option value="10">10</option></select><div style="display: flex;margin-top: 10px;"><button style="margin-bottom: 20px" onclick="getValue()">确定</button><button style="margin-left: 10px;margin-bottom: 20px" onclick="closeLayer()">取消</button></div></div>'})}})}window.PLOTLYENV=window.PLOTLYENV||{},window.PLOTLYENV.BASE_URL="https://plot.ly","scattermapbox"==data[0].type&&(data.splice(1,0,{type:"scattermapbox",lat:[],lon:[],mode:"markers",marker:{size:10,color:"purple"},text:[],textposition:"top left",hoverinfo:"text",name:"评分高于8分"}),separateOutScoreMoreThanEightInit(),data[0].marker.colorscale&&(data[0].showlegend=!1,data[1].showlegend=!1)),Plotly.newPlot("chartId",data,layout,{showLink:!1,linkText:"Export to plot.ly"});var myPlot=document.getElementById("chartId"),index1=0,index2=0,index=0,indexx=0;set(myPlot);</script></body></html>'''
    # python True False 转换成 js的true false
    template = template.replace('True', 'true').replace('False', 'false')
    with open(fileName, 'w', encoding='utf-8') as f:
        f.write(template)

if __name__ == '__main__':
    pass