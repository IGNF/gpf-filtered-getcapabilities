token=null
compteur=0
while [ "$token" == "null" ] && [[ $compteur != 10 ]]
do
	sleep 5
 	compteur=$((compteur+1))

	user=`curl --request POST \
	  	  --url https://sso.geopf.fr/realms/geoplateforme/protocol/openid-connect/token \
		  --header "content-type: application/x-www-form-urlencoded" \
		  -d 'client_id='$1'&client_secret='$2'&grant_type=client_credentials'`

	token=`echo $user | jq '.access_token' | cut -d'"' -f2`
done

for dossier in `ls dist`
do
	echo $dossier
	for fichier in `ls dist/$dossier`
	do
		echo $fichier
		resultat=`curl --request GET \
		  --url "https://data.geopf.fr/api/datastores/2d4dd9f5-ce16-4e7f-81d5-7e392209b7ff/annexes?limit=1&path=/$dossier/$fichier" \
		  --header "Authorization: Bearer $token"`
		
		id_annexe=`echo $resultat | jq '.[0]._id' | cut -d'"' -f2`
  		echo $id_annexe
		if [[ "$id_annexe" == "null" ]]
  		then
  			new_annexe=curl --request POST \
  			--url https://data.geopf.fr/api/datastores/2d4dd9f5-ce16-4e7f-81d5-7e392209b7ff/annexes \
  			--header "Authorization: Bearer $token" \
  			--header 'content-type: multipart/form-data' \
  			--form file=@dist/$dossier/$fichier \
  			--form paths=/$dossier/$fichier

     			id_annexe=`echo $new_annexe | jq '_id' | cut -d'"' -f2`

     			curl --request PATCH \
  			--url https://data.geopf.fr/api/datastores/2d4dd9f5-ce16-4e7f-81d5-7e392209b7ff/annexes/$id_annexe \
  			--header "Authorization: Bearer $token" \
  			--header 'content-type: application/json' \
  			--data '{"published": true}'

       		else
  
			curl --request PUT \
  			--url https://data.geopf.fr/api/datastores/2d4dd9f5-ce16-4e7f-81d5-7e392209b7ff/annexes/$id_annexe \
  			--header "Authorization: Bearer $token" \
  			--header 'Content-Type: multipart/form-data' \
  			--form file=@dist/$dossier/$fichier
     		fi
  	done
done
