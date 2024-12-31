DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'habr') THEN
      CREATE DATABASE habr;
   END IF;
END $$;
