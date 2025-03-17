from authentication.models import Group

def get_group_hierarchy(group):
    """
    Recursive function to build the group hierarchy.
    Starts from the group and traverses up to the parent.
    """
    # Base case: if no parent, return just the current group name
    if not group.parent_id:
        return group.group_name
    
    # Get the parent group object
    parent_group = Group.objects.filter(group_id=group.parent_id).first()
    
    # Recursively get the parent's hierarchy
    parent_hierarchy = get_group_hierarchy(parent_group) if parent_group else ""
    
    # Combine the parent's hierarchy with the current group name
    return f"{parent_hierarchy} > {group.group_name}"

def seed():
    print("🔹 Menjalankan Group Seeder...")

    # Hapus data lama
    Group.objects.all().delete()

    # Buat Group
    Group.objects.create(group_id="1", group_name="PT  Anugrah Nusantara Jaya", status="active")
    Group.objects.create(group_id="2", group_name="PT Putra Kahayan Abadi", status="active")
    Group.objects.create(group_id="3", group_name="PT Nusantara Jaya Raya Mujur", status="active")
    Group.objects.create(group_id="4", group_name="PT Karunia Anugrah Nusantara", status="active")
    Group.objects.create(group_id="5", group_name="PT Nusa Unggul Sarana Adicipta", status="active")
    Group.objects.create(group_id="6", group_name="PT Anugrah Nusantara Jaya", status="active")

    # Buat Child Group
    Group.objects.create(group_id="7", group_name="Branch Samarinda", parent_id="1", status="active")
    Group.objects.create(group_id="8", group_name="Branch Balikpapan", parent_id="1", status="active")
    Group.objects.create(group_id="9", group_name="Branch Palangkaraya", parent_id="2", status="active")
    Group.objects.create(group_id="10", group_name="Branch Sampit", parent_id="2", status="active")
    Group.objects.create(group_id="11", group_name="Branch Pangkalan Bun", parent_id="2", status="active")
    Group.objects.create(group_id="12", group_name="Branch Banjarmasin", parent_id="3", status="active")
    Group.objects.create(group_id="13", group_name="Branch Makaasar", parent_id="4", status="active")
    Group.objects.create(group_id="14", group_name="Branch Semarang", parent_id="5", status="active")
    Group.objects.create(group_id="15", group_name="Branch Demak", parent_id="5", status="active")
    Group.objects.create(group_id="16", group_name="Branch Pati", parent_id="5", status="active")
    Group.objects.create(group_id="17", group_name="Branch Sukoharjo", parent_id="5", status="active")
    Group.objects.create(group_id="18", group_name="Branch Yogyakarta", parent_id="5", status="active")
    Group.objects.create(group_id="19", group_name="Branch Surabaya", parent_id="6", status="active")

    # Buat Child Group Departement
    Group.objects.create(group_id="20", group_name="Departement HRD", parent_id="7", status="active")
    Group.objects.create(group_id="21", group_name="Departement Marketing", parent_id="7", status="active")
    Group.objects.create(group_id="22", group_name="Departement Finance", parent_id="7", status="active")
    Group.objects.create(group_id="23", group_name="Departement HRD", parent_id="8", status="active")
    Group.objects.create(group_id="24", group_name="Departement Marketing", parent_id="8", status="active")
    Group.objects.create(group_id="25", group_name="Departement Finance", parent_id="8", status="active")
    Group.objects.create(group_id="26", group_name="Departement HRD", parent_id="9", status="active")
    Group.objects.create(group_id="27", group_name="Departement Marketing", parent_id="9", status="active")
    Group.objects.create(group_id="28", group_name="Departement Finance", parent_id="9", status="active")
    Group.objects.create(group_id="29", group_name="Departement HRD", parent_id="10", status="active")
    Group.objects.create(group_id="30", group_name="Departement Marketing", parent_id="10", status="active")
    Group.objects.create(group_id="31", group_name="Departement Finance", parent_id="10", status="active")
    Group.objects.create(group_id="32", group_name="Departement HRD", parent_id="11", status="active")
    Group.objects.create(group_id="33", group_name="Departement Marketing", parent_id="11", status="active")
    Group.objects.create(group_id="34", group_name="Departement Finance", parent_id="11", status="active")
    Group.objects.create(group_id="35", group_name="Departement HRD", parent_id="12", status="active")
    Group.objects.create(group_id="36", group_name="Departement Marketing", parent_id="12", status="active")
    Group.objects.create(group_id="37", group_name="Departement Finance", parent_id="12", status="active")
    Group.objects.create(group_id="38", group_name="Departement HRD", parent_id="13", status="active")
    Group.objects.create(group_id="39", group_name="Departement Marketing", parent_id="13", status="active")
    Group.objects.create(group_id="40", group_name="Departement Finance", parent_id="13", status="active")
    Group.objects.create(group_id="41", group_name="Departement HRD", parent_id="14", status="active")
    Group.objects.create(group_id="42", group_name="Departement Marketing", parent_id="14", status="active")
    Group.objects.create(group_id="43", group_name="Departement Finance", parent_id="14", status="active")
    Group.objects.create(group_id="44", group_name="Departement HRD", parent_id="15", status="active")
    Group.objects.create(group_id="45", group_name="Departement Marketing", parent_id="15", status="active")
    Group.objects.create(group_id="46", group_name="Departement Finance", parent_id="15", status="active")
    Group.objects.create(group_id="47", group_name="Departement HRD", parent_id="16", status="active")
    Group.objects.create(group_id="48", group_name="Departement Marketing", parent_id="16", status="active")
    Group.objects.create(group_id="49", group_name="Departement Finance", parent_id="16", status="active")
    Group.objects.create(group_id="50", group_name="Departement HRD", parent_id="17", status="active")
    Group.objects.create(group_id="51", group_name="Departement Marketing", parent_id="17", status="active")
    Group.objects.create(group_id="52", group_name="Departement Finance", parent_id="17", status="active")
    Group.objects.create(group_id="53", group_name="Departement HRD", parent_id="18", status="active")
    Group.objects.create(group_id="54", group_name="Departement Marketing", parent_id="18", status="active")
    Group.objects.create(group_id="55", group_name="Departement Finance", parent_id="18", status="active")
    Group.objects.create(group_id="56", group_name="Departement HRD", parent_id="19", status="active")
    Group.objects.create(group_id="57", group_name="Departement Marketing", parent_id="19", status="active")
    Group.objects.create(group_id="58", group_name="Departement Finance", parent_id="19", status="active")

    # Buat Child Group Jabatan
    Group.objects.create(group_id="59", group_name="Jabatan Direktur", parent_id="20", status="active")
    Group.objects.create(group_id="60", group_name="Jabatan Manager", parent_id="20", status="active")
    Group.objects.create(group_id="61", group_name="Jabatan Staff", parent_id="20", status="active")
    Group.objects.create(group_id="62", group_name="Jabatan Direktur", parent_id="21", status="active")
    Group.objects.create(group_id="63", group_name="Jabatan Manager", parent_id="21", status="active")
    Group.objects.create(group_id="64", group_name="Jabatan Staff", parent_id="21", status="active")
    Group.objects.create(group_id="65", group_name="Jabatan Direktur", parent_id="22", status="active")
    Group.objects.create(group_id="66", group_name="Jabatan Manager", parent_id="22", status="active")
    Group.objects.create(group_id="67", group_name="Jabatan Staff", parent_id="22", status="active")
    Group.objects.create(group_id="68", group_name="Jabatan Direktur", parent_id="23", status="active")
    Group.objects.create(group_id="69", group_name="Jabatan Manager", parent_id="23", status="active")
    Group.objects.create(group_id="70", group_name="Jabatan Staff", parent_id="23", status="active")
    Group.objects.create(group_id="71", group_name="Jabatan Direktur", parent_id="24", status="active")
    Group.objects.create(group_id="72", group_name="Jabatan Manager", parent_id="24", status="active")
    Group.objects.create(group_id="73", group_name="Jabatan Staff", parent_id="24", status="active")
    Group.objects.create(group_id="74", group_name="Jabatan Direktur", parent_id="25", status="active")
    Group.objects.create(group_id="75", group_name="Jabatan Manager", parent_id="25", status="active")
    Group.objects.create(group_id="76", group_name="Jabatan Staff", parent_id="25", status="active")
    Group.objects.create(group_id="77", group_name="Jabatan Direktur", parent_id="26", status="active")
    Group.objects.create(group_id="78", group_name="Jabatan Manager", parent_id="26", status="active")
    Group.objects.create(group_id="79", group_name="Jabatan Staff", parent_id="26", status="active")
    Group.objects.create(group_id="80", group_name="Jabatan Direktur", parent_id="27", status="active")
    Group.objects.create(group_id="81", group_name="Jabatan Manager", parent_id="27", status="active")
    Group.objects.create(group_id="82", group_name="Jabatan Staff", parent_id="27", status="active")
    Group.objects.create(group_id="83", group_name="Jabatan Direktur", parent_id="28", status="active")
    Group.objects.create(group_id="84", group_name="Jabatan Manager", parent_id="28", status="active")
    Group.objects.create(group_id="85", group_name="Jabatan Staff", parent_id="28", status="active")
    Group.objects.create(group_id="86", group_name="Jabatan Direktur", parent_id="29", status="active")
    Group.objects.create(group_id="87", group_name="Jabatan Manager", parent_id="29", status="active")
    Group.objects.create(group_id="88", group_name="Jabatan Staff", parent_id="29", status="active")
    Group.objects.create(group_id="89", group_name="Jabatan Direktur", parent_id="30", status="active")
    Group.objects.create(group_id="90", group_name="Jabatan Manager", parent_id="30", status="active")
    Group.objects.create(group_id="91", group_name="Jabatan Staff", parent_id="30", status="active")
    Group.objects.create(group_id="92", group_name="Jabatan Direktur", parent_id="31", status="active")
    Group.objects.create(group_id="93", group_name="Jabatan Manager", parent_id="31", status="active")
    Group.objects.create(group_id="94", group_name="Jabatan Staff", parent_id="31", status="active")
    Group.objects.create(group_id="95", group_name="Jabatan Direktur", parent_id="32", status="active")
    Group.objects.create(group_id="96", group_name="Jabatan Manager", parent_id="32", status="active")
    Group.objects.create(group_id="97", group_name="Jabatan Staff", parent_id="32", status="active")
    Group.objects.create(group_id="98", group_name="Jabatan Direktur", parent_id="33", status="active")
    Group.objects.create(group_id="99", group_name="Jabatan Manager", parent_id="33", status="active")

    for group in Group.objects.all():
        group.group_hierarchy = get_group_hierarchy(group)
        group.save()

    print("✅ Group Seeder selesai!")

