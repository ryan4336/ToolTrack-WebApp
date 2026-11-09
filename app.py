            raise ValueError(
                f"Missing CSV columns: {', '.join(sorted(missing))}"
            )

        tools_to_add = []
        csv_asset_tags = set()
        csv_serial_numbers = set()

        # Load existing identifiers once instead of querying
        # the database separately for every CSV row.
        existing_asset_tags = set(
            db.session.scalars(db.select(Tool.asset_tag)).all()
        )

        existing_serial_numbers = set(
            db.session.scalars(
                db.select(Tool.serial_number)
                .where(Tool.serial_number.isnot(None))
            ).all()
        )

        for row in csv_reader:

            row_number = csv_reader.line_num

            asset_tag = (row["asset_tag"] or "").strip()
            tool_name = (row["tool_name"] or "").strip()
            brand = (row["brand"] or "").strip() or None
            model = (row["model"] or "").strip() or None
            serial_number = (
                (row["serial_number"] or "").strip() or None
            )
            condition = (row["condition"] or "").strip() or None
            notes = (row["notes"] or "").strip() or None

            purchase_date_text = (
                (row["purchase_date"] or "").strip()
            )

            if purchase_date_text:
                purchase_date = datetime.strptime(
                    purchase_date_text, "%m/%d/%Y"
                ).date()
            else:
                purchase_date = None

            price_text = (row["price"] or "").strip()
            price = Decimal(price_text) if price_text else None

            if not asset_tag or not tool_name:
                raise ValueError(
                    f"Missing asset tag or tool name on row {row_number}"
                )

            if asset_tag in existing_asset_tags:
                raise ValueError(
                    f"Asset tag {asset_tag} already exists."
                )

            if asset_tag in csv_asset_tags:
                raise ValueError(
                    f"Duplicate asset tag {asset_tag} in CSV."
                )

            if serial_number:
                if serial_number in existing_serial_numbers:
                    raise ValueError(
                        f"Serial number {serial_number} already exists."
                    )

                if serial_number in csv_serial_numbers:
                    raise ValueError(
                        f"Duplicate serial number {serial_number} in CSV."
                    )

                csv_serial_numbers.add(serial_number)

            csv_asset_tags.add(asset_tag)

            tool = Tool(
                asset_tag=asset_tag,
                tool_name=tool_name,
                brand=brand,
                model=model,
                serial_number=serial_number,
                purchase_date=purchase_date,
                price=price,
                condition=condition,
                notes=notes,
                status="Available"
            )

            tools_to_add.append(tool)

        # Insert all tools in one transaction
        db.session.add_all(tools_to_add)
        db.session.commit()

        flash(
            f"Successfully imported {len(tools_to_add)} tools.",
            "success"
        )

    except (ValueError, InvalidOperation) as error:
        db.session.rollback()
        flash(f"Import failed: {error}", "error")

    except Exception as error:
        db.session.rollback()
        print("IMPORT ERROR:", error, flush=True)
        flash(f"Import failed: {error}", "error")

    return redirect(url_for("tool_inventory"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
