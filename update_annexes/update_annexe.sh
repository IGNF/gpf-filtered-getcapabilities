token=null
compteur=0
while [ "$token" == "null" ] && [[ $compteur != 10 ]]
do
	sleep 5
 	compteur=$((compteur+1))
	totp=`python3 update_annexes/totp.py --totp_key $3`

	user=`curl --request POST \
	  	  --url https://sso.geopf.fr/realms/geoplateforme/protocol/openid-connect/token \
		  --header "content-type: application/x-www-form-urlencoded" \
		  -d 'client_id=gpf-warehouse&username='$1'&password='$2'&client_secret=BK2G7Vvkn7UDc8cV7edbCnHdYminWVw2&grant_type=password&totp='$totp`

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
		
		curl --request PUT \
  --url https://data.geopf.fr/api/datastores/2d4dd9f5-ce16-4e7f-81d5-7e392209b7ff/annexes/$id_annexe \
  --header "Authorization: Bearer $token" \
  --header 'Content-Type: multipart/form-data' \
  --form file=@dist/$dossier/$fichier
  	done
done
