import json
import codecs
import jieba.posseg as pseg



output_filename = '../../data/taobao_trial_result_matched.csv'
input_filename = '../../data/taobao_trial_result.dat'
describe_type_filename = '../../data/describe_type.txt'
cluster_filename = '../../data/kmeans_result_sorted_cluster.txt'

fout = codecs.open(output_filename,'w','utf8')
fout.write('"id","time","money","status","alipay_desc","tb_desc","tb_type","tb_quantity","tb_province","tb_city","alipay_count","tb_count","huabei_available","taobaoLevel","huabei_quota","category"\n')
flog = codecs.open('log.txt', 'w', 'utf8')


# load_types 
cluster_to_category = json.loads(codecs.open('cates_whole.txt','r','utf8').readline())
cluster_to_category_temp = dict()
for item in cluster_to_category:
	cluster_to_category_temp[int(item)] = cluster_to_category[item]
cluster_to_category = cluster_to_category_temp
cluster = dict()
for line in codecs.open(cluster_filename,'r','utf8'):
	[word,clus] = line.split()
	pos = word.rfind('/')
	word = word[:pos]
	clus = int(clus)
	cluster[word] = clus
def get_taobao_desc_type(desc):
	if type(desc) != type(u'inicode-string'):
		return '-1'
	words = [word.word for word in pseg.cut(desc)]
	weight = [0 for i in range(13)]
	for word in words:
		if word in cluster:
			if cluster_to_category[cluster[word]]== -1:
				continue
			weight[cluster_to_category[cluster[word]]] += 1
	maxcnt = 0
	argmax = -1
	for i in range(13):
		if maxcnt < weight[i]:
			maxcnt = weight[i]
			argmax = i
	return str(argmax)



describe_type = dict()
def load_describe_type(filename):
	for line in codecs.open(filename, 'r', 'utf8'):
		try:
			[item, cate] = line.split()
		except:
			print line
		describe_type[item] = cate

load_describe_type('../../data/describe_type.txt')
print 'loaded describe type'

def analysis(taobao_orders, alipay_bills, cid, taobaoLevel, huabeiedu, huabeiAvailable):
	ret = False
	for it in alipay_bills: # normalize alipay bills
		if type(it['trans_desc']) != type(u'string'):
			it['trans_desc'] = str(it['trans_desc'])
		pos = it['status'].find(' ')
		if pos != -1:
			it['status'] = it['status'][:pos]
	black_namelist = set()
	for item in taobao_orders: # normalize taobao trans firstly
		if type(item['type']) != type(u'string'):
			item['type'] = str(item['type'])
		if type(item['describe']) != type(u'string'):
			item['describe'] = str(item['describe'])
		if type(item['province']) != type(u'string'):
			item['province'] = str(item['province'])
		if type(item['city']) != type(u'string'):
			item['city'] = str(item['city'])
		if type(huabeiedu) != type('string'):
			huabeiedu = str(huabeiedu)
		if type(huabeiAvailable) != type('string'):
			huabeiAvailable = str(huabeiAvailable)
		if type(taobaoLevel) != type(u'string'):
			taobaoLevel = str(taobaoLevel)
		## normalization done
		
		taobao_desc = item['describe']
		taobao_count = 0
		taobao_trans_time = item['trans_time'][:-3]
		if (taobao_desc, taobao_trans_time, item['price']) in black_namelist:
			continue
		else:
			black_namelist.add((taobao_desc, taobao_trans_time, item['price']) )
		for i in range(len(taobao_orders)):
			if taobao_orders[i]['describe'] == taobao_desc and taobao_orders[i]['trans_time'][:-3] == taobao_trans_time:
				taobao_count += 1
		successful_matched = False
		flog.write('taobao ' + taobao_trans_time + '\n')
		for it in alipay_bills:
			alipay_trans_time = it['trans_time'][:-3]
			if taobao_trans_time == alipay_trans_time and -it['money'] == item['price'] and item['status']==it['status']:
				if taobao_desc not in describe_type:
					describe_type[taobao_desc] = get_taobao_desc_type(taobao_desc)
				alipay_desc = it['trans_desc']
				alipay_count = 0
				for i in range(len(alipay_bills)):
					if alipay_bills[i]['trans_desc'] == alipay_desc and alipay_bills[i]['trans_time'][:-3] == alipay_trans_time:
						alipay_count += 1
				fout.write('"'+str(cid)+'",' # cid
				+'"'+taobao_trans_time+'",' # time
				+'"'+str(item['price'])+'",' # money
				+'"'+it['status']+'",' # status
				+'"'+it['trans_desc']+'",' # ali_desc
				+'"'+item['describe']+'",' # tb_desc
				+'"'+item['type']+'",' # type
				+'"'+str(item['quantity'])+'",' #quantity
				+'"'+item['province']+'",' # tb_province
				+'"'+item['city']+'",' # tb_city
				+'"'+str(alipay_count)+'",' # alipay_count
				+'"'+str(taobao_count)+'",' # tb_count
				+'"'+huabeiAvailable+'",' #huabei_available
				+'"'+taobaoLevel+'",' # taobaoleve;
				+'"'+huabeiedu+'",' # huabeiedu
				+'"'+describe_type[taobao_desc]+'"' #category
				+'\n')
				# print taobao_trans_time, alipay_trans_time, it['money'], item['price']
				ret = True
				successful_matched = True
		if not successful_matched:
			if taobao_desc not in describe_type:
				describe_type[taobao_desc] = get_taobao_desc_type(taobao_desc)
			fout.write('"'+str(cid)+'",' # cid
			+'"'+taobao_trans_time+'",' # time
			+'"'+str(item['price'])+'",' # money
			+'"'+' '+'",' # status
			+'"'+' '+'",' # ali_desc
			+'"'+item['describe']+'",' # tb_desc
			+'"'+item['type']+'",' # type
			+'"'+str(item['quantity'])+'",' #quantity
			+'"'+item['province']+'",' # tb_province
			+'"'+item['city']+'",' # tb_city
			+'"'+str(0)+'",' # alipay_count
			+'"'+str(taobao_count)+'",' # tb_count
			+'"'+huabeiAvailable+'",' #huabei_available
			+'"'+taobaoLevel+'",' # taobaoleve;
			+'"'+huabeiedu+'",' # huabeiedu
			+'"'+describe_type[taobao_desc]+'"' #category
			+'\n')

	return ret


for cnt,line in enumerate(open(input_filename)):
	data = json.loads(line)
	analysis(data['taobao_orders'], data['alipay_bills'], data['cid'], data['taobaoLevel'], data['huabeiedu'], data['huabeiAvailable'])
	print cnt

fout.close()
flog.close()
