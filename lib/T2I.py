import matplotlib.pyplot as plt
import skimage.io as io
import glove
import cca
import numpy as np

#dataDir ='~/coco/images/'
dataDir = '../coco-master/images/'
dataType = 'val2014'

def softmax(scores):
    # scores is a dict {id:score}
    somme = 0
    for key in scores.keys():
        scores[key] = np.exp(scores[key])
        somme += scores[key]
    for key in scores.keys():
        scores[key] /= float(somme)

def display_top_img(tag, score_dict, number):
#Display top number images
    ids = score_dict.keys()
    score = score_dict.values()
    index = np.argsort(score)
    for i in range(number):
        I = io.imread(dataDir + dataType + '/COCO_' + dataType + '_%012d' % ids[index[len(index)-i-1]] + '.jpg')
        nb = i + 1
        io.imsave('output/' + tag + '_top%d' %nb, I)

def display_top_tag(score_dict, number):
    #Display top number tags
    cats = score_dict.keys()
    score = score_dict.values()
    index = np.argsort(score)
    print("Top %d tags retrieved from image" %number)
    for i in range(number):
        print(cats[index[len(index)-1-i]] + ' %f' % score[index[len(index)-1-i]])

def search_img(img_feat,img_feats):
    output = {}
    for key in img_feats.keys():
        # need to normalize the vectors
        img_feat_tmp = img_feat.copy() / np.linalg.norm(img_feat)
        img_feats_tmp = img_feats[key].copy() / np.linalg.norm(img_feats[key])

        output[key] = np.dot(img_feat_tmp,img_feats_tmp).item()
    return output

def search_tag(tag_feat,tag_feats, coco):
    output = {}
    cats = {}
    for idx in tag_feats.keys():
        annIds = coco.getAnnIds(imgIds=idx)
        anns = coco.loadAnns(annIds)
        for ann in anns:
            instance = coco.loadCats(ann['category_id'])[0]['name']
            if instance in cats.keys():
                np.vstack((cats[instance],tag_feats[idx]))
            else:
                cats[instance] = tag_feats[idx]
    for key in cats.keys():
        # need to normalize the vectors
        cat_feat_tmp = tag_feat.copy() / np.linalg.norm(tag_feat)
        cat_feats_tmp = cats[key].copy() / np.linalg.norm(cats[key])
        output[key] = np.dot(cat_feat_tmp,cat_feats_tmp).item()
    return output

def tag2image(tag, cca_object, glove_object, test_img_feat):
    # retrieve the tag vector
    tag_vector = glove_object.vec_expression(tag)

    # predict with CCA
    img_vector = cca_object.predict(tag_vector)

    # search image
    scores = search_img(img_vector,test_img_feat)

    return scores

def perso_tag2image(tag, cca_object, glove_object, img_feats):
    # retrieve the tag vector
    tag_vector = glove_object.vec_expression(tag)

    output = {}
    for key in img_feats.keys():
        output[key] = cca_object.sim(tag_vector,img_feats[key])

    return output

def perso_image2tag_qualitative(image_path, cca_object, cnn_object, test_tag_feat, coco):
    # retrieve the image feature vector
    _,_,img_vector,_ = cnn_object.extractFeatures(image_path)

    # calculate score in latent space
    scores = {}
    cats = {}
    for idx in test_tag_feat.keys():
        annIds = coco.getAnnIds(imgIds=idx)
        anns = coco.loadAnns(annIds)
        for ann in anns:
            instance = coco.loadCats(ann['category_id'])[0]['name']
            if instance in cats.keys():
                np.vstack((cats[instance],test_tag_feat[idx]))
            else:
                cats[instance] = test_tag_feat[idx]
    for key in cats.keys():
        scores[key] = cca_object.sim_I2T(img_vector,cats[key])

    softmax(scores)

    return scores

def perso_image2tag_quantitative(image_vector, cca_object, test_tag_feat, coco):
    # calculate score in latent space
    scores = {}
    cats = {}
    for idx in test_tag_feat.keys():
        annIds = coco.getAnnIds(imgIds=idx)
        anns = coco.loadAnns(annIds)
        for ann in anns:
            instance = coco.loadCats(ann['category_id'])[0]['name']
            if instance in cats.keys():
                np.vstack((cats[instance],test_tag_feat[idx]))
            else:
                cats[instance] = test_tag_feat[idx]
    for key in cats.keys():
        scores[key] = cca_object.sim_I2T(image_vector,cats[key])

    softmax(scores)

    return scores
