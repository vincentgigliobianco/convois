import pysal 
import numpy as np
from geopy.distance import geodesic

def get_voisins_with_kdtree(epsilon_param, df, dict_datetimes_h_param):
    # Ce dictionnaire va contenir les résultats pour chaque date t en utilisant les (lat,long)
    dict_pts_found = {}
    # Ce dictionnaire va contenir les résultats pour chaque date t en utilisant les id des véhicules
    dict_pts_found_with_id = {}


    # On boucle pour chaque date t
    # for t in range(0,len(all_datetimes)):
    for h in dict_datetimes_h_param.values():
        # Extraction de tous les couples (latitude, longitude)
        locations_temp_with_id = []

        #if h == datetime(2019, 5, 4, 4, 45, 40):
        df_temp = df[df["date_and_time"] == h]
        locations_temp_with_id = [(row.id,row.lat, row.long) for row in df_temp.itertuples()]

        #print ("valeur de h:", h)
        #print ("nb de véhicules obtenus chaque 5 minute:", len(locations_temp_with_id))

        # Création d'un dictionnaire avec clé = (lat, long) et valeur = id
        dict_corresp = {}
        for triplet in locations_temp_with_id:
            dict_corresp[triplet[1],triplet[2]] = triplet[0]

        locations_temp_without_id = [each[1:3] for each in locations_temp_with_id]

        # Pour chaque (latitude, longitude) extraite, 
        # extraction de tous les points situés à moins de epsilon mètres

        dict_pts_found[h] = {}
        locations_temp = locations_temp_without_id.copy()

        k = 0
        while len(locations_temp) > 1: 

            if k < len(locations_temp):
                current_point = locations_temp[k]
            else:
                # print ("ON A TRAITE TOUS LES POINTS")
                break
            k += 1
            # print ("On traite current_point:", current_point)


            # Création de l'arbre grâce à KDTree
            tree = pysal.lib.cg.kdtree.KDTree(locations_temp, distance_metric='Arc', radius=pysal.lib.cg.RADIUS_EARTH_KM)
            indices = tree.query_ball_point(current_point, epsilon_param)

            # Extraction des points
            # print ("Pour le point: ", current_point, "il y a : ", \
            # len([locations_temp_without_id[j] for j in indices if locations_temp_without_id[j] != current_point]))

            nb_values_to_add = 0 

            #locations_temp_modified = []
            dict_pts_found[h][current_point] = []

            for j in indices:

                if current_point != locations_temp[j] and nb_values_to_add == 0:    

                    if locations_temp[j] not in dict_pts_found[h][current_point]:
                        dict_pts_found[h][current_point].append(locations_temp[j])

                elif current_point != locations_temp[j] and nb_values_to_add > 0:    

                    if locations_temp[j] not in dict_pts_found[h][current_point]:
                        dict_pts_found[h][current_point].append(locations_temp[j])

                nb_values_to_add += 1

            del indices


        # !!! FIN DE LA BOUCLE "pour chaque timestamp" !!!
        dict_pts_found_with_id[h] = {}


        # Maintenant, dédoublonnage des listes de véhicules obtenues
        # pour chaque timestamp

        liste_id_done_all = []
        for k,v in dict_pts_found[h].items():

            liste_id_todo_sorted = []

            # récupération d'un id de véhicule correspondant à un "current_point"
            new_key = dict_corresp[k] 
            # récupération de la liste d'id de véhicules correspondant aux points voisins d'un current point
            new_value = [dict_corresp[each] for each in v if each != []]

            liste_id_todo = new_value.copy()
            liste_id_todo.append(new_key)
            liste_id_todo_sorted = sorted(liste_id_todo)


            # alimentation dans "dict_pts_found_with_id[h]" que si les éléments n'ont pas déjà été alimentés
            if new_value != [] and liste_id_todo_sorted not in liste_id_done_all:

                dict_pts_found_with_id[h][new_key] = new_value

                liste_id_done = new_value.copy()
                liste_id_done.append(new_key)
                liste_id_done_sorted = sorted(liste_id_done)
                liste_id_done_all.append(liste_id_done_sorted)

        del dict_corresp
        
    return dict_pts_found_with_id


# Intersection 
def intersect(l1,l2):
    resultat = []
    
    if type(l1) == list and type(l2) == list:
        for each_1 in l1:
            for each_2 in l2:
                if each_1 == each_2:
                    resultat.append(each_1)
   
    return resultat


def get_intersection(liste_1, liste_2):
    #print ("liste_1",liste_1)
    #print ("liste_2",liste_2)
    
    if liste_1 == [] or liste_2 == []:
        resultat = []
    elif liste_1 == [] and liste_2 == []:
        resultat = []
    
    elif type(liste_1) == list and type(liste_2) == list:

        resultat = []

        for l in liste_1:
            for k in liste_2:
                #print ("listes:",l, k)
                #print ("intersect(l, k)",intersect(l, k))
                
                if intersect(l, k) != [] and len(intersect(l, k)) > 1:
                    #print ("intersection non vide entre ",l, "et", k) 
                    del resultat
                    resultat = intersect(l, k)
                    break
            else:
                continue
            break
                        
    return resultat


def create_lists_timestamp(id_t1,dict_dates_to_id_param, dict_pts_found_with_id_param):
    dict_all_id = {}
    
    # Calcul de la date qui suit t1
    t1 = [k for k,v in dict_dates_to_id_param.items() if v == id_t1][0]
    
    id_t1_next = id_t1 + 2
    t1_next = [k for k,v in dict_dates_to_id_param.items() if v == id_t1_next - 1][0]
         
    #print ("On traite les identifiants succcessifs: ",id_t1, id_t1_next - 1)
    #print ("correspondant aux dates :",t1, t1_next)
    
    key_value = list(dict_pts_found_with_id_param.items())[id_t1:id_t1_next]
    #print ("key_value",key_value)
      
    #dict_all_id[key_value[0][0]] = key_value[0][1]
    #dict_all_id[key_value[1][0]] = key_value[1][1]
    
    # On veut gérer le nombre variable de liste de points situés dans un même voisinage
    dict_all_id[key_value[0][0]] = key_value[0][1]
    dict_all_id[key_value[1][0]] = key_value[1][1]
         
    return dict_all_id


# La date t1 = date de début et t2 = date qui suit t1
def get_all_convois(t1, t2, dict_dates_to_id_param, dict_pts_found_with_id_param):
    
    #print ("\n La date t1 vaut:", t1)
    #print ("La date t2 vaut:", t2)
    
    # calcul de id_t1 et id_t2
    id_t1 = dict_dates_to_id_param[t1]

    #TEST
    #id_t2 = dict_dates_to_id_param[t2]
    
    # Agrégation :
            
    # On ne considère pas la notion de durée h de convoi
    # On prend h = 5 minutes

    dict_successive_id = create_lists_timestamp(id_t1,dict_dates_to_id_param,dict_pts_found_with_id_param)
    
    #print ("dict_successive_id",dict_successive_id)

    dict_one = list(dict_successive_id.items())[0][1].copy()
    dict_two = list(dict_successive_id.items())[1][1].copy()

    #print ("dict_one",dict_one)
    #print ("dict_two",dict_two)
    
    if dict_one != {}:
        liste_one = []
        # chaque élément key, value est transformé en liste
        for k,v in dict_one.items():
            # k est un id de véhicule
            # v est une liste d'id de véhicules (de la forme v = [45,7,16])
            liste_one_temp = v.copy()
            liste_one_temp.append(k)
            liste_one.append(liste_one_temp)
    else:
        liste_one = []
        
    if dict_two != {}:
        liste_two = []
        # chaque élément key, value est transformé en liste
        for k,v in dict_two.items():
            liste_two_temp = v.copy()
            liste_two_temp.append(k)
            liste_two.append(liste_two_temp)
    else:
        liste_two = [] 
      
    #print ("\n date t1",t1)  
    #print ("liste_one",liste_one)
    #print ("liste_two",liste_two)

    # on associe toutes les combinaisons de deux listes deux à deux 
    # et on extrait les intersections non vides 
    resultat = get_intersection(liste_one, liste_two)

    return resultat

def get_intersection_final_result(liste_1, liste_2):
    #print ("liste_1",liste_1)
    #print ("liste_2",liste_2)
    
    if liste_1 == [] or liste_2 == []:
        resultat = []
    elif liste_1 == [] and liste_2 == []:
        resultat = []
    
    elif type(liste_1) == list and type(liste_2) == list:
        liste_1_sorted = sorted(liste_1)
        liste_2_sorted = sorted(liste_2)
        if len(intersect(liste_1_sorted, liste_2_sorted)) > 1:
            resultat = intersect(liste_1_sorted, liste_2_sorted)
        else:
            resultat = []     
                    
    return resultat

def get_final_result(dict_temp_result,pas):
    resultat = {}
    for k,v in dict_temp_result.items():
            
        p = 0

        # Valeur "fake" = 45 pour faire démarrer le "while"
        intersect_result = [45]
        while intersect_result != []:
            
            if p == 0:
                intersect_result = v
                #del intersect_result
                k_kept = k[0]
                p += 1
            else:
                # calcul du triplet 
                # - dates qui suivent k[0] égales à   k[0] + un multiple de pas = 5 minutes
                # - dates qui suivent k[1] égales à   k[1] + un multiple de pas = 5 minutes
                next_k_0 = k[0] + p*pas
                next_k_1 = k[1] + p*pas
                
                #  k[2] = intervalle de 5 minutes = datetime.timedelta(0, 300)
                next_k = (next_k_0,next_k_1,k[2])

                # On utilise le résultat correspondant au triplet next_k présent dans le résultat dict_temp_result
                # On calcule l'intersection entre la liste de véhicules à la date t et celle à la date t + 1
                
                # On sort toutes les intersections de listes non vides entre deux dates t et t + 1 
                if next_k in dict_temp_result.keys() and dict_temp_result[next_k] != None:

                    # intersection entre v et dict_temp_result[next_k]
                    intersect_result = get_intersection_final_result(intersect_result,dict_temp_result[next_k])
                    if intersect_result != []:
                        resultat[k_kept,next_k_1] = intersect_result
                    p += 1
                else:
                    p += 1
                    break
            
    return resultat


def get_convoi_with_vitesse(df_param,resultat_final_param,v_seuil):

    resultat = {}

    for k,v in resultat_final_param.items():

        random_id_list = np.random.randint(len(v),size = 1)
        random_id = v[random_id_list[0]]

        # (lat,long) du point random_id à la date k[0]
        lat_0 = df_param[(df_param["id"] == random_id) & (df_param["date_and_time"] == k[0])]["lat"].values[0]
        long_0 = df_param[(df_param["id"] == random_id) & (df_param["date_and_time"] == k[0])]["long"].values[0]

        #print ("lat_0", lat_0)
        #print ("long_0", long_0)

        pt_0 = (lat_0, long_0)
        # (lat,long) du point random_id à la date k[1]
        lat_1 = df_param[(df_param["id"] == random_id) & (df_param["date_and_time"] == k[1])]["lat"].values[0]
        long_1 = df_param[(df_param["id"] == random_id) & (df_param["date_and_time"] == k[1])]["long"].values[0]
        pt_1 = (lat_1, long_1)

        # Distance entre ces 2 points
        distance = geodesic(pt_0,pt_1).kilometers
        #print ("distance", distance)

        # Durée entre ces 2 points
        duration = (k[1] - k[0]).total_seconds()  / 3600
        #print ("duration", duration)

        # Vitesse du point random_id
        vitesse  = distance/duration
        #print ("vitesse", vitesse, "pour convoi trouvé", v)
    

        if vitesse >= v_seuil:
            print (v, "avec vitesse ", round(vitesse), "km/h et entre les dates: ",k[0],"et ",k[1])
            resultat[k] = v  
    return resultat


