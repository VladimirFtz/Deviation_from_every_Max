


import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import seaborn as sns

str1 = []
folder = []
All_Secs_list = []
strings_counter_list = []



# Считываем дынные для дальнейшей работы
for i in os.walk('D:\Торговля\Код\Анализ 7000 Акций США\Пример_1'):   # Путь к папке с файлами котировок!!!
    folder.append(i)

stocks_counter = 0
for address, dirs, files in folder:         # Проходим по всем файлам акций в папке подвыборки
    for file in files:
        my_file = open(address+'/'+file, mode= "r")
        
        One_Sec_list = []
        strings_counter = 0
        for i, line in enumerate(my_file):
            if i > 0:
                l = line.rstrip()
                Date,Open,High,Low,Close,Volume,OpenInt = l.split(",")
                #Date= l.split(",")
                listInter = (Open,High,Low,Close,Volume,OpenInt,Date)  # Создание списка по отдельной строке
                # Добавил Date в конец
                
                One_Sec_list.append(listInter)  # Создание  списка всех Свечей текстового файла.
                strings_counter = strings_counter + 1
        
        my_file.close()
        All_Secs_list.append(One_Sec_list)
        strings_counter_list.append(strings_counter)
        stocks_counter = stocks_counter + 1
        
All_Secs = np.array(All_Secs_list)     
stocks_count = All_Secs.shape[0]
print('stocks_count: ', stocks_count)

otkl_min = 10
otkl_max = 95
otkl_step = 5

vihod_min = 10
vihod_max = 250
vihod_step = 10


counter = 0
stopper = False
write_results_by_otkl = False
results_by_secs = []
for k in range(0, stocks_count):
    results_by_otkl = []
    current_sec = np.array(All_Secs[k])
    days_count = current_sec.shape[0] - 1
    best_price = 0
    exitFlag=False
    if days_count < vihod_max + 1:           # Если дней котировок акции меньше vihod_max, то пропускаем.
        next                                 # Работала нормально но в одном моменте как будто next не выходит
                                             # а цикл продолжается, очень странно.
        
    for otkl in range(otkl_min, otkl_max + 1, otkl_step):      # Перебираем различные отклонения
        stopper = False
        comulative_results_by_vihod = np.zeros(int((vihod_max - vihod_min)/vihod_step + 1))
        divider = 0
        for i in range(1, days_count + 1 - vihod_max):
            current_price = np.float(current_sec[i,0])
            if i == 1:
                best_price = current_price
                stopper = False
            if current_price > best_price:
                best_price = current_price
                stopper = False
            if current_price < np.float(current_sec[i-1,0])*0.57: # Фильтр от дробления (сплитов)
                best_price = current_price
                stopper = False
            if best_price > 0:
                my_string = current_sec[i,6]
                year = int(my_string[0:4])
                if year != 2008 and year != 2009:            # Убираем 2008 и 2009 года потому что они дают оч хорош результат
                    if (best_price - current_price) / best_price * 100 > otkl and stopper == False:
                        counter = counter + 1
                        stopper = True
                        results_by_vihod = []
                        for l in range(vihod_min, vihod_max + 1, vihod_step):     # Перебор дней до выхода
                            later_price = np.float(current_sec[i + l, 0])
                            current_result = (later_price - current_price)/current_price * 100
                            if current_result < 400:
                                results_by_vihod.append(current_result)       #Фильтр для слишком больших выбросов
                            else:
                                results_by_vihod.append(0)
                        
                        comulative_results_by_vihod = comulative_results_by_vihod + np.array(results_by_vihod)
                        divider = divider + 1
                        write_results_by_otkl = True     # Добавлено чтобы не записывать когда нет сделок в просматриваемой акции
                    
        if write_results_by_otkl == True:     
            comulative_results_by_vihod = comulative_results_by_vihod / divider
            results_by_otkl.append(comulative_results_by_vihod)
        write_results_by_otkl = False
                    #results_by_otkl.append(comulative_results_by_vihod)
                    
                    #break
            #if i > days_count - vihod_max - vihod_step:       # Выход из цикла otkl как только первого откл
            #    exitFlag=True                                 # не будет найдено.
                
        #if (exitFlag):
        #    break
    
    results_by_secs.append(np.array(results_by_otkl))
    

results_by_secs = np.array(results_by_secs)
    
secs_num = results_by_secs.shape[0] 

deals_profit = np.zeros((int((otkl_max - otkl_min) / otkl_step + 1), int((vihod_max - vihod_min) / vihod_step + 1)))
deals_loss = np.zeros((int((otkl_max - otkl_min) / otkl_step + 1), int((vihod_max - vihod_min) / vihod_step + 1)))
deals_count = np.zeros((int((otkl_max - otkl_min) / otkl_step + 1), int((vihod_max - vihod_min) / vihod_step + 1)))             

      
for i in range(0, secs_num):
    for j in range(0, int((otkl_max - otkl_min) / otkl_step + 1)):
        if j >= results_by_secs[i].shape[0]:
            break
        for k in range(0, int((vihod_max - vihod_min) / vihod_step + 1)):
            if results_by_secs[i][j][k] >= 0 and results_by_secs[i][j][k] < 400:   # Фильтр от возможных выбросов
                deals_profit[j][k] = deals_profit[j][k] + results_by_secs[i][j][k]
                deals_count[j][k] = deals_count[j][k] + 1
            if results_by_secs[i][j][k] < 0:
                deals_loss[j][k] = deals_loss[j][k] + results_by_secs[i][j][k]
                deals_count[j][k] = deals_count[j][k] + 1
         

overal_profit = deals_profit + deals_loss
mean_profit = overal_profit / deals_count
P_E = -deals_profit / deals_loss

otkl_list = np.arange(otkl_min, otkl_max + 1, otkl_step)
vihod_list = np.arange(vihod_min, vihod_max + 1, vihod_step) 

deals_loss = np.transpose(deals_loss)
deals_loss = pd.DataFrame(deals_loss)
deals_loss.columns = [otkl_list]

deals_profit = np.transpose(deals_profit)
deals_profit = pd.DataFrame(deals_profit)
deals_profit.columns = [otkl_list]

mean_profit = np.transpose(mean_profit)
mean_profit = pd.DataFrame(mean_profit)
mean_profit.columns = [otkl_list]

overal_profit = np.transpose(overal_profit)
overal_profit = pd.DataFrame(overal_profit)
overal_profit.columns = [otkl_list]

P_E = np.transpose(P_E)
P_E = pd.DataFrame(P_E)
P_E.columns = [otkl_list]

deals_count = np.transpose(deals_count)
deals_count = pd.DataFrame(deals_count)
deals_count.columns = [otkl_list]
#P_E.rename(vihod_dict)


#sns.heatmap(mean_profit, annot=True)
print('All_Max:')

print('mean_profit:')
print(mean_profit)
print('P_E:')
print(P_E)
print('deals_count:')
print(deals_count)
print('counter:')
print(counter)
    


