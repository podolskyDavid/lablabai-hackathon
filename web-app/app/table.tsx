import React from "react";

interface CSVTableProps {
  data: Record<string, string>[];
}

const CSVTable: React.FC<CSVTableProps> = ({ data }) => {
  const headers = data.length > 0 ? Object.keys(data[0]) : [];

  return (
    <div className="mt-4">
      {data.length === 0 ? (
        <p>No data available.</p>
      ) : (
        <table className="w-full border-collapse border rounded overflow-hidden shadow-md">
          <thead>
            <tr>
              {headers.map((header, index) => (
                <th
                  key={index}
                  className="py-2 px-4 bg-blue-500 text-white font-semibold border-b"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr key={index} className="border-b">
                {headers.map((header, columnIndex) => (
                  <td
                    key={columnIndex}
                    className="py-2 px-4 border"
                  >
                    {row[header]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default CSVTable;
