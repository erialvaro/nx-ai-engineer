-- Row Level Security policies for {{project_title}}.
-- Principle: a user only sees and mutates their own rows. The service-role key
-- (server-side) bypasses RLS for trusted backend operations.

-- Read own rows
create policy "items_select_own"
    on public.items for select
    using (auth.uid() = owner_id);

-- Insert rows you own
create policy "items_insert_own"
    on public.items for insert
    with check (auth.uid() = owner_id);

-- Update own rows
create policy "items_update_own"
    on public.items for update
    using (auth.uid() = owner_id)
    with check (auth.uid() = owner_id);

-- Delete own rows
create policy "items_delete_own"
    on public.items for delete
    using (auth.uid() = owner_id);
