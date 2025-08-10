DATE=$(date +%F)
echo "Making backup of kino database on $DATE..."
pg_dump -h $KINO_HOST -U kino -d kino -W > kino-backup-$DATE.sql
echo "Written backup to kino-backup-$DATE.sql"
