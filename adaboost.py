import statistics
import math
import pandas as pd
import numpy as np
from numpy import log
from pprint import pprint
import matplotlib.pyplot as plt

def branches(df,columns):
    att_barnches={}
    for att in columns:
        x=df[att].unique()
        att_barnches[att]=x.tolist()
    return(att_barnches)

def entropy_H_GI(fraction, H_M_GI):
    if fraction==0:
        entropy=0
        # print('xxxx entropy is ', entropy)
    elif H_M_GI == 'H':
        entropy= -(fraction)*math.log(fraction)
    elif H_M_GI == 'GI':
        entropy= -(fraction)**2
    return entropy

def IG(df, att, H_M_GI):
    label_vars =df.label.unique()

    #entropy of whole:
    entropy_s=0
    list_M_S=[]
    for labels in label_vars:
        # num= len(df['label'][df.label== labels])
        num=df.loc[df['label']==labels]['weight'].sum()
        num=round(num,6)
        # den = len(df.label)
        den=df.loc[:,'weight'].sum()
        den=round(den,6)
        # print('den', den , 'num', num , labels)
        if num==0 or den==0:
            frac_s=0
        else:
            frac_s=(num/(den))
        #print(num,den)
        if H_M_GI == 'M':
            list_M_S.append(frac_s)
        else:
            entropy_s += entropy_H_GI(frac_s, H_M_GI)
            # print('entropy_s',entropy_s,'\n')
    if H_M_GI == 'GI':
        entropy_s= 1+entropy_s
    if H_M_GI == 'M':
        entropy_s= 1-max(list_M_S)
    # print('entropy_s',entropy_s)
    # if entropy_s<0 :
        # print(df)

    #entropy of each attribute:
    features=df[att].unique()
    entropy_sigma=0
    #loop over features of each attribute including [job,age,...]
    for feat in features:
        entropy_att=0
        # M
        if H_M_GI == 'M':
            list_M=[]
            #loop over labels of each features to find majority
            for label_var in label_vars:
                # num = len(df[att][df[att]==feat][df.label ==label_var2])
                df_temp=df.loc[df[att]==feat]
                num=df_temp.loc[df_temp.label ==label_var]['weight'].sum()
                num=round(num,6)
                # den = len(df[att][df[att]==feat])
                den=df.loc[df[att]==feat]['weight'].sum()
                den=round(den,6)
                if den==0:
                    frac=0
                else:
                    frac = num/(den)
                list_M.append(frac)
                #print(list_M)
            entropy_att = 1-max(list_M)

        # H or GI :
        else:
            #loop over labels of each features
            for label_var in label_vars:
                # num= len(df[att][df[att]==feat][df.label ==label_var])
                df_temp=df.loc[df[att]==feat]
                num=df_temp.loc[df_temp.label ==label_var]['weight'].sum()
                num=round(num,6)

                # den = len(df[att][df[att]==feat])
                den=df.loc[df[att]==feat]['weight'].sum()
                den=round(den,6)
                # print( 'feat', feat ,'label_var\n',label_var,'num', num ,'den',den)
                # print("\n")
                if num==0 or den==0:
                    frac=0
                else:
                    frac = num/(den)
                entropy_att += entropy_H_GI(frac,H_M_GI)
            #Gini Index:
            if H_M_GI == 'GI':
                entropy_att= 1+entropy_att

        #sum entropy of a feature
        frac_sigma = den/len(df)
        entropy_sigma += frac_sigma*entropy_att
        # print('entropy of',feat, entropy_att,frac_sigma)
    InformationGain = entropy_s- entropy_sigma
    # print('InformationGain',InformationGain,'\n')
    return InformationGain

def choose_node (IG_dict):
    max_IG=0
    #print(IG_dict)
    for attribute in IG_dict:
        if max_IG<=IG_dict[attribute]:
            max_IG=IG_dict[attribute]
            choosen=attribute
        # else:
        #     print(attribute,IG_dict[attribute])

    return choosen

def subtable (df,node,branch):
    df_sub=(df[df[node]==branch].reset_index(drop=True))
    return df_sub

def common_func(df):
    x=df.label.unique()
    weight1=df.loc[df['label']==x[0]]['weight'].sum()
    weight2=df.loc[df['label']==x[1]]['weight'].sum()
    if weight1>weight2:
        return x[0]
    else:
        return x[1]

def ID3_func(df,depth,H_M_GI,att_barnches,remain_att,main_tree=None,tree=None):

    attributes=[]
    attributes= df.keys()[:-2]
    # print(attributes)

    if len(df.label.unique())==1 :
        return df.label[0]

    if depth == 0 and main_tree==None:
        common_label= common_func(df)
        return common_label

    #collecting IG of attributes
    else:
        IG_dict={}
        for att in remain_att:
            inf_gain = IG(df, att, H_M_GI)
            IG_dict[att]=inf_gain

        #finding the node
        root_node=choose_node(IG_dict)
        remain_att=remain_att.drop(root_node)

        #draw tree
        if tree is None:
            tree={}
            tree[root_node]={}

        #check the depth and main_tree
        if depth == 0 and main_tree==True:
            tree[root_node]=common_func(df)
            return tree

        depth=depth-1

        #finding subtable
        node_branches=[]
        node_branches=att_barnches[root_node]
        for branch in node_branches:
            df_sub= subtable (df,root_node,branch)
            if len (df_sub) == 0:
                tree[root_node][branch]=common_func(df)
            else:
                tree[root_node][branch] =ID3_func(df_sub,depth,H_M_GI,att_barnches,remain_att)
    #pprint (tree)
    return tree

def predict(tree, df_row,max_depth):
    for key1 in tree.keys():
        if type(tree[key1]) is not dict:
            predict_label=tree[key1]
            return predict_label
        else:
            tree2=tree[key1]
            for key2 in tree2.keys():
                if type(tree2[key2]) is not dict:
                    if df_row[key1]== key2:
                        predict_label =tree2[key2]
                else:
                    if df_row[key1]==key2:
                        tree3=tree2[key2]
                        predict_label=predict(tree3, df_row, max_depth)
    return predict_label

def test(df,tree,max_depth):
    right=0
    for row in range (0,df.shape[0]):
         #print(row)
         df_rows = df.iloc[row , : ]
         #print(df_rows)
         pr_label= predict(tree,df_rows,max_depth)
         #print(pr_label)
         if pr_label==df_rows.label:
             right+=1
    error=(df.shape[0]-right)/df.shape[0]
    return  error

def data_modify(df):
    #attributes=[]
    #attributes= df.keys()[:-1]
    #print(attributes)
    med_list=[]
    for col in df.keys()[:-1]:
        if col== 'pdays':
            df= df.astype({'pdays': 'float'})
            df= df.replace({'pdays':-1.0}, 'unknown' )
            #med= df.loc[:,'pdays'].median(skipna=True)
            for row in range(0,df.shape[0]):
                if (df.loc[row,col])!='unknown':
                    med_list.append(df.loc[row,col])
            med=statistics.median(med_list)
            #print(col,med)
            for row in range(0,df.shape[0]):
                    if (df.loc[row,col])!='unknown':
                        if (df.loc[row,col])<med:
                            df.loc[row,col]=0
                        else:
                            df.loc[row,col]=1
        else:
            #x=df.loc[:,col].unique()
            if df.loc[1,col].isdigit()== True:
                df=df.astype({col: 'float'})
                med= df.loc[:,col].median(skipna=True)
                # print(col,med)
                for row in range(0,df.shape[0]):
                    if (df.loc[row,col])<=med:
                        df.loc[row,col]=0
                    else:
                        df.loc[row,col]=1
        df=df.replace({'label':'yes'},'+1')
        df=df.replace({'label':'no'},'-1')
        df= df.astype({'label': 'int32'})
        # print (df)
    return df

def vote(df,tree,max_depth):
    epsilon=0

    for row in range (0,df.shape[0]):
         df_rows = df.iloc[row , : ]
         #predict label
         pr_label= predict(tree,df_rows,max_depth)
         #Accuracy calculation
         if pr_label!=df_rows.label:
             epsilon+= df.loc[row ,'weight']

    #calculate mistake and alpha for voting
    alpha=1/2*math.log((1-epsilon)/epsilon)
    #modifying weight column
    for row in range (0,df.shape[0]):
         df_rows = df.iloc[row , : ]
         pr_label= predict(tree,df_rows,max_depth)
         # print('pr_label',pr_label, 'real_label', df_rows.label)
         # print(pr_label*df_rows.label)
         # x=np.exp(-alpha*(pr_label*df_rows.label))
         D=df.loc[row,'weight']*np.exp(-alpha*(pr_label*df_rows.label))
         # label_real=df_rows.label
         df.loc[row,'weight']=D
    Z=df.loc[:,'weight'].sum()
    # print('sum of weights', Z)
    df.loc[:,'weight']=df.loc[:,'weight']/Z
    # print('sum normalized' ,df.loc[:,'weight'].sum())
    return  epsilon, alpha , df

def Adaboost(df_train,df_test, T , max_depth,Entropy_method,att_barnches):
    error_test_list=[]
    error_stumps_test_list=[]
    error_train_list=[]
    error_stumps_train_list=[]
    epsilon_list=[]
    H_test=np.zeros(df_test.shape[0])
    H_train=np.zeros(df_train.shape[0])
    df_train.loc[:,'weight']=1/len(df_train.index)
    #print(df_train)
    for t in range (1,T+1):
        remain_att=[]
        remain_att=df_train.keys()[:-2]
        tree = ID3_func(df_train, max_depth, Entropy_method,att_barnches,remain_att, main_tree=True)
        epsilon, alpha , df_train = vote(df_train, tree, max_depth)
        epsilon_list.append(epsilon)

        #testing df_test
        correct_test=0
        correct_stump_test=0
        for row in range (0,df_test.shape[0]):
          df_rows_test = df_test.iloc[row , : ]
          h_test=predict(tree, df_rows_test,max_depth)
          #predict Adaboost
          H_test[row]= H_test[row] + h_test*alpha
          pr_label_test=int(np.sign(H_test[row]))
          if pr_label_test==0:
              pr_label_test=+1
          if pr_label_test==df_rows_test.label:
              correct_test+=1
          #predict decision stump
          if h_test != df_rows_test.label:
            correct_stump_test+=1
        #error adaboost
        error_test=(df_test.shape[0]-correct_test)/df_test.shape[0]
        error_test_list.append(error_test)
        #error decision stump
        error_stump_test=(df_test.shape[0]-correct_stump_test)/df_test.shape[0]
        error_stumps_test_list.append(error_stump_test)
        print ("T", t , 'error_test', error_test,'error_stump_test', error_stump_test,'\n')

        #testing df_train
        correct_train=0
        correct_stump_train=0
        for row in range (0,df_train.shape[0]):
          df_rows_train = df_train.iloc[row , : ]
          h_train=predict(tree, df_rows_train,max_depth)
          #predict Adaboost
          H_train[row]= H_train[row] + h_train*alpha
          pr_label_train=int(np.sign(H_train[row]))
          if pr_label_train==0:
              pr_label_train=+1
          if pr_label_train==df_rows_train.label:
              correct_train+=1
          #predict decision stump
          if h_train != df_rows_train.label:
            correct_stump_train+=1
        #error adaboost
        error_train=(df_train.shape[0]-correct_train)/df_train.shape[0]
        error_train_list.append(error_train)
        #error decision stump
        error_stump_train=(df_train.shape[0]-correct_stump_train)/df_train.shape[0]
        error_stumps_train_list.append(error_stump_train)
        print ("T", t , 'error_train', error_train,'error_stump_train', error_stump_train,'\n')
    return error_test_list ,error_stumps_test_list , error_train_list, error_stumps_train_list

#Main body
columns=['age','job','marital','education','default','balance','housing',
         'loan','contact','day', 'month', 'duration', 'campaign', 'pdays',
         'previous', 'poutcome', 'label']
data_train=[]
tree={}
data_test=[]

#train
train_file= open ( 'train.csv' , 'r' )
for line in train_file:
    terms= line.strip().split(',')
    data_train.append (terms)
df_train= pd.DataFrame(data_train,columns=columns)
#test
test_file= open ( 'test.csv' , 'r' )
for line in test_file:
    terms= line.strip().split(',')
    data_test.append (terms)
df_test= pd.DataFrame(data_test,columns=columns)

#modify with unknown
df_train_m=data_modify(df_train)
df_test_M=data_modify(df_test)

#adding weight to dataset
df_train_m.insert(len(df_train_m.columns),'weight',1)

#finding attribute branches
att_barnches=branches(df_train_m,columns)

#hyperparameters
max_depth=1
Entropy_method='H'
error_list=[]
T=500

error_test_list ,error_stumps_test_list , error_train_list, error_stumps_train_list = Adaboost(df_train_m,df_test_M, T , max_depth,Entropy_method,att_barnches)
#print('error_stumps_list',error_stumps_list,'\nerror_list', error_list,'\n')

plt.title('Adaboost error of T = {}'.format(T) )
plt.plot(range(1,T+1),error_test_list)
plt.plot(range(1,T+1),error_train_list)
plt.legend(["test", "train"])
plt.show()

plt.title('error_stumps_list')
plt.plot(range(1,T+1),error_stumps_test_list)
plt.plot(range(1,T+1),error_stumps_train_list)
plt.legend(["test", "train"])
plt.show()
