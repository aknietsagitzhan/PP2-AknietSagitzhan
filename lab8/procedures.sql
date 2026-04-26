CREATE OR REPLACE PROCEDURE upsert_contact(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(p_names, 1)
    LOOP
        IF p_phones[i] ~ '^\d{11}$' THEN
            
            IF EXISTS (SELECT 1 FROM contacts WHERE name = p_names[i]) THEN
                UPDATE contacts
                SET phone = p_phones[i]
                WHERE name = p_names[i];
            ELSE
                INSERT INTO contacts(name, phone)
                VALUES (p_names[i], p_phones[i]);
            END IF;

        ELSE
            RAISE NOTICE 'Invalid phone: %', p_phones[i];
        END IF;
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_name IS NOT NULL THEN
        DELETE FROM contacts WHERE name = p_name;
    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM contacts WHERE phone = p_phone;
    END IF;
END;
$$;